"""Bounded Ollama adapter for one statically configured local model."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import ipaddress
import json
import time
from types import MappingProxyType
from urllib.parse import urlsplit

import httpx

from ..inference_contracts import (
    FailureCode,
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
    MAX_DURATION_MS,
    MAX_JSON_BYTES,
)
from ..provider import (
    InferenceProvider,
    ProviderDescriptor,
    ProviderRuntimeKind,
)


APPROVED_MODEL_ID = "qwen2.5:1.5b-instruct-q4_K_M"
APPROVED_TIMEOUT_CEILING_MS = 120_000
APPROVED_KEEP_ALIVE = "5m"
PROVIDER_ID = "ollama-local"
MAX_INSTRUCTION_LENGTH = 4_096

SchemaResolver = Callable[[str], Mapping[str, object]]
SchemaValidator = Callable[[str, Mapping[str, object]], None]


@dataclass(frozen=True, slots=True)
class OllamaProviderConfig:
    """Immutable configuration for one approved local Ollama model."""

    base_url: str
    model_id: str
    timeout_ceiling_ms: int
    keep_alive: str

    def __post_init__(self) -> None:
        if type(self.base_url) is not str:
            raise TypeError("base_url must be a string")
        try:
            parsed = urlsplit(self.base_url)
            port = parsed.port
        except ValueError as error:
            raise ValueError("base_url is malformed") from error
        if parsed.scheme != "http":
            raise ValueError("base_url scheme must be http")
        if not parsed.hostname or port is None:
            raise ValueError("base_url requires an explicit host and port")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("base_url must not contain credentials")
        if parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise ValueError("base_url contains prohibited components")
        host = parsed.hostname
        if host != "localhost":
            try:
                address = ipaddress.ip_address(host)
            except ValueError as error:
                raise ValueError("base_url host must be local or private") from error
            if (
                not (address.is_private or address.is_loopback)
                or address.is_unspecified
                or address.is_multicast
            ):
                raise ValueError("base_url host must be local or private")
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))

        if type(self.model_id) is not str:
            raise TypeError("model_id must be a string")
        if self.model_id != APPROVED_MODEL_ID:
            raise ValueError("model_id is not the approved model")
        if type(self.timeout_ceiling_ms) is not int:
            raise TypeError("timeout_ceiling_ms must be an integer")
        if self.timeout_ceiling_ms != APPROVED_TIMEOUT_CEILING_MS:
            raise ValueError("timeout_ceiling_ms must be 120000")
        if type(self.keep_alive) is not str:
            raise TypeError("keep_alive must be a string")
        if self.keep_alive != APPROVED_KEEP_ALIVE:
            raise ValueError("keep_alive must be 5m")


class OllamaInferenceProvider(InferenceProvider):
    """Translate one bounded Brain request to one local Ollama invocation."""

    def __init__(
        self,
        config: OllamaProviderConfig,
        client: httpx.AsyncClient,
        schema_resolver: SchemaResolver,
        schema_validator: SchemaValidator,
    ) -> None:
        if not isinstance(config, OllamaProviderConfig):
            raise TypeError("config must be an OllamaProviderConfig")
        if not isinstance(client, httpx.AsyncClient):
            raise TypeError("client must be an httpx.AsyncClient")
        if not callable(schema_resolver):
            raise TypeError("schema_resolver must be callable")
        if not callable(schema_validator):
            raise TypeError("schema_validator must be callable")
        self._config = config
        self._client = client
        self._schema_resolver = schema_resolver
        self._schema_validator = schema_validator
        self._descriptor = ProviderDescriptor(
            provider_id=PROVIDER_ID,
            model_id=config.model_id,
            runtime_kind=ProviderRuntimeKind.LOCAL,
            capabilities=(InferenceCapability.STRUCTURED_INFERENCE,),
        )

    @property
    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        started_ns = time.monotonic_ns()
        if not isinstance(request, InferenceRequest):
            raise TypeError("request must be an InferenceRequest")

        try:
            instruction, data = _validate_payload(request)
        except (TypeError, ValueError):
            return self._failure(
                request, FailureCode.INVALID_REQUEST, "invalid inference request", started_ns
            )

        try:
            resolved_schema = self._schema_resolver(request.output_schema_ref)
            provider_schema = _plain_bounded_mapping(resolved_schema)
        except Exception:
            return self._failure(
                request, FailureCode.INVALID_REQUEST, "unapproved output schema", started_ns
            )

        rendered = instruction + "\n\nInput JSON:\n" + json.dumps(
            _plain_json(data),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        body = {
            "model": self._config.model_id,
            "messages": [{"role": "user", "content": rendered}],
            "stream": False,
            "format": provider_schema,
            "keep_alive": self._config.keep_alive,
        }
        timeout_seconds = (
            min(request.timeout_ms, self._config.timeout_ceiling_ms) / 1_000
        )

        try:
            async with asyncio.timeout(timeout_seconds):
                response = await self._client.post(
                    f"{self._config.base_url}/api/chat",
                    json=body,
                    timeout=httpx.Timeout(timeout_seconds),
                )
            response.raise_for_status()
        except httpx.ConnectError:
            return self._failure(
                request,
                FailureCode.RUNTIME_UNAVAILABLE,
                "local inference runtime unavailable",
                started_ns,
            )
        except (httpx.TimeoutException, TimeoutError):
            return self._failure(
                request, FailureCode.TIMEOUT, "inference deadline exceeded", started_ns
            )
        except httpx.HTTPError:
            return self._failure(
                request, FailureCode.PROVIDER_FAILURE, "provider request failed", started_ns
            )

        if len(response.content) > MAX_JSON_BYTES:
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )
        try:
            envelope = response.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )
        if not isinstance(envelope, Mapping):
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )

        model = envelope.get("model")
        done = envelope.get("done")
        if not isinstance(model, str) or type(done) is not bool:
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )
        if model != self._config.model_id or done is not True:
            return self._failure(
                request, FailureCode.PROVIDER_FAILURE, "provider response incomplete", started_ns
            )
        message = envelope.get("message")
        if not isinstance(message, Mapping) or not isinstance(
            message.get("content"), str
        ):
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )

        try:
            structured_output = json.loads(
                message["content"], parse_constant=_reject_json_constant
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )
        if not isinstance(structured_output, Mapping):
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "malformed provider output", started_ns
            )
        try:
            self._schema_validator(request.output_schema_ref, structured_output)
        except Exception:
            return self._failure(
                request, FailureCode.MALFORMED_OUTPUT, "output schema mismatch", started_ns
            )

        try:
            return InferenceResult(
                schema_version=request.schema_version,
                correlation_id=request.correlation_id,
                request_id=request.request_id,
                success=True,
                failure_code=None,
                structured_output=structured_output,
                provider_id=PROVIDER_ID,
                model_id=self._config.model_id,
                duration_ms=_duration_ms(started_ns),
                failure_detail=None,
                warnings=(),
            )
        except (TypeError, ValueError):
            return self._failure(
                request,
                FailureCode.MALFORMED_OUTPUT,
                "malformed provider output",
                started_ns,
            )

    def _failure(
        self,
        request: InferenceRequest,
        code: FailureCode,
        detail: str,
        started_ns: int,
    ) -> InferenceResult:
        return InferenceResult(
            schema_version=request.schema_version,
            correlation_id=request.correlation_id,
            request_id=request.request_id,
            success=False,
            failure_code=code,
            structured_output=None,
            provider_id=PROVIDER_ID,
            model_id=self._config.model_id,
            duration_ms=_duration_ms(started_ns),
            failure_detail=detail,
            warnings=(),
        )


def _validate_payload(
    request: InferenceRequest,
) -> tuple[str, Mapping[str, object]]:
    if request.capability is not InferenceCapability.STRUCTURED_INFERENCE:
        raise ValueError("unsupported capability")
    payload = request.input_payload
    if frozenset(payload) != frozenset(("instruction", "data")):
        raise ValueError("input_payload must contain exactly instruction and data")
    instruction = payload["instruction"]
    data = payload["data"]
    if type(instruction) is not str:
        raise TypeError("instruction must be a string")
    if (
        not 1 <= len(instruction) <= MAX_INSTRUCTION_LENGTH
        or instruction.isspace()
        or instruction != instruction.strip()
    ):
        raise ValueError("instruction is invalid")
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping")
    return instruction, data


def _plain_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _plain_json(item) for key, item in value.items()}
    if type(value) is tuple:
        return [_plain_json(item) for item in value]
    return value


def _plain_bounded_mapping(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("resolved schema must be a mapping")
    plain = _plain_json(value)
    encoded = json.dumps(
        plain,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(encoded) > MAX_JSON_BYTES:
        raise ValueError("resolved schema is too large")
    return plain  # type: ignore[return-value]


def _duration_ms(started_ns: int) -> int:
    elapsed = max(0, (time.monotonic_ns() - started_ns) // 1_000_000)
    return min(elapsed, MAX_DURATION_MS)

def _reject_json_constant(value: str) -> object:
    raise ValueError("non-finite JSON constant")
