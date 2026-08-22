from __future__ import annotations

import ast
import asyncio
from collections.abc import Mapping
from dataclasses import FrozenInstanceError, fields
import inspect
import json
from pathlib import Path
from typing import cast

import httpx
import pytest

from core.brain.inference_contracts import (
    FailureCode,
    InferenceCapability,
    InferenceRequest,
)
from core.brain.provider import ProviderRuntimeKind
from core.brain.providers.ollama import (
    OllamaInferenceProvider,
    OllamaProviderConfig,
)


ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = ROOT / "core" / "brain" / "providers" / "ollama.py"
MODEL_ID = "qwen2.5:1.5b-instruct-q4_K_M"
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["category", "confidence"],
    "properties": {
        "category": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
}


def make_config(**overrides: object) -> OllamaProviderConfig:
    values: dict[str, object] = {
        "base_url": "http://10.0.0.2:11434",
        "model_id": MODEL_ID,
        "timeout_ceiling_ms": 120_000,
        "keep_alive": "5m",
    }
    values.update(overrides)
    return OllamaProviderConfig(**values)  # type: ignore[arg-type]


def make_request(**overrides: object) -> InferenceRequest:
    values: dict[str, object] = {
        "schema_version": 1,
        "correlation_id": "correlation-1",
        "request_id": "request-1",
        "capability": InferenceCapability.STRUCTURED_INFERENCE,
        "input_payload": {
            "instruction": "Classify the input.",
            "data": {"z": 1, "a": {"é": True}},
        },
        "timeout_ms": 30_000,
        "output_schema_ref": "classification_v1",
        "input_reference": None,
        "context_references": (),
    }
    values.update(overrides)
    return InferenceRequest(**values)  # type: ignore[arg-type]


def valid_response(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        request=request,
        json={
            "model": MODEL_ID,
            "done": True,
            "message": {
                "role": "assistant",
                "content": '{"category":"normal","confidence":0.95}',
            },
            "ignored": "transient",
        },
    )


def make_provider(
    handler: object = valid_response,
    *,
    resolver: object | None = None,
    validator: object | None = None,
    config: OllamaProviderConfig | None = None,
) -> tuple[OllamaInferenceProvider, httpx.AsyncClient]:
    transport = httpx.MockTransport(handler)  # type: ignore[arg-type]
    client = httpx.AsyncClient(transport=transport)
    provider = OllamaInferenceProvider(
        config or make_config(),
        client,
        cast(object, resolver) if resolver is not None else lambda ref: SCHEMA,
        cast(object, validator) if validator is not None else lambda ref, value: None,
    )
    return provider, client


def run_infer(provider: OllamaInferenceProvider, request: InferenceRequest | None = None):
    return asyncio.run(provider.infer(request or make_request()))


def test_config_is_frozen_slotted_and_has_exact_fields() -> None:
    config = make_config()
    assert not hasattr(config, "__dict__")
    assert [field.name for field in fields(config)] == [
        "base_url",
        "model_id",
        "timeout_ceiling_ms",
        "keep_alive",
    ]
    with pytest.raises(FrozenInstanceError):
        config.keep_alive = "1m"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("base_url", "normalized"),
    [
        ("http://10.0.0.2:11434", "http://10.0.0.2:11434"),
        ("http://172.31.63.2:11434/", "http://172.31.63.2:11434"),
        ("http://127.0.0.1:11434", "http://127.0.0.1:11434"),
        ("http://localhost:11434", "http://localhost:11434"),
        ("http://[fd00::2]:11434", "http://[fd00::2]:11434"),
    ],
)
def test_private_and_local_base_urls_are_accepted(
    base_url: str, normalized: str
) -> None:
    assert make_config(base_url=base_url).base_url == normalized


@pytest.mark.parametrize(
    "base_url",
    [
        "https://10.0.0.2:11434",
        "http://8.8.8.8:11434",
        "http://example.com:11434",
        "http://0.0.0.0:11434",
        "http://10.0.0.2",
        "http://user:pass@10.0.0.2:11434",
        "http://10.0.0.2:11434?x=1",
        "http://10.0.0.2:11434#fragment",
        "http://10.0.0.2:11434/path",
        "not-a-url",
        "http://[broken:11434",
    ],
)
def test_public_malformed_or_prohibited_base_urls_are_rejected(
    base_url: str,
) -> None:
    with pytest.raises(ValueError):
        make_config(base_url=base_url)


@pytest.mark.parametrize("base_url", [None, 1, b"http://10.0.0.2:11434"])
def test_non_string_base_url_is_rejected(base_url: object) -> None:
    with pytest.raises(TypeError):
        make_config(base_url=base_url)


def test_model_timeout_and_keep_alive_are_exactly_bound() -> None:
    config = make_config()
    assert config.model_id == MODEL_ID
    assert config.timeout_ceiling_ms == 120_000
    assert config.keep_alive == "5m"
    for overrides in (
        {"model_id": "other"},
        {"timeout_ceiling_ms": 1},
        {"timeout_ceiling_ms": True},
        {"keep_alive": "1m"},
    ):
        with pytest.raises((TypeError, ValueError)):
            make_config(**overrides)


def test_descriptor_is_exact_and_immutable() -> None:
    provider, _ = make_provider()
    descriptor = provider.descriptor
    assert descriptor.provider_id == "ollama-local"
    assert descriptor.model_id == MODEL_ID
    assert descriptor.runtime_kind is ProviderRuntimeKind.LOCAL
    assert descriptor.capabilities == (
        InferenceCapability.STRUCTURED_INFERENCE,
    )
    with pytest.raises(FrozenInstanceError):
        descriptor.model_id = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    "payload",
    [
        {"data": {}},
        {"instruction": "Do it."},
        {"instruction": "Do it.", "data": {}, "extra": True},
        {"instruction": "", "data": {}},
        {"instruction": "   ", "data": {}},
        {"instruction": " leading", "data": {}},
        {"instruction": "trailing ", "data": {}},
        {"instruction": "x" * 4_097, "data": {}},
        {"instruction": 1, "data": {}},
        {"instruction": "Do it.", "data": []},
        {"instruction": "Do it.", "data": {}, "model": MODEL_ID},
        {"instruction": "Do it.", "data": {}, "options": {}},
    ],
)
def test_invalid_payloads_fail_before_schema_or_http(payload: object) -> None:
    calls: list[str] = []

    def resolver(ref: str) -> Mapping[str, object]:
        calls.append("resolver")
        return SCHEMA

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append("http")
        return valid_response(request)

    provider, _ = make_provider(handler, resolver=resolver)
    result = run_infer(provider, make_request(input_payload=payload))
    assert result.failure_code is FailureCode.INVALID_REQUEST
    assert result.structured_output is None
    assert calls == []


def test_empty_and_nested_data_are_accepted() -> None:
    provider, _ = make_provider()
    assert run_infer(
        provider,
        make_request(input_payload={"instruction": "Do it.", "data": {}}),
    ).success
    assert run_infer(
        provider,
        make_request(
            input_payload={
                "instruction": "Do it.",
                "data": {"nested": {"items": [1, True, None]}},
            }
        ),
    ).success


def test_nan_is_rejected_by_inference_request_before_adapter() -> None:
    with pytest.raises(ValueError):
        make_request(
            input_payload={"instruction": "Do it.", "data": {"value": float("nan")}}
        )


def test_rendering_and_request_body_are_exact() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return valid_response(request)

    provider, _ = make_provider(handler)
    result = run_infer(provider)
    assert result.success
    assert len(captured) == 1
    outbound = captured[0]
    assert outbound.method == "POST"
    assert str(outbound.url) == "http://10.0.0.2:11434/api/chat"
    body = json.loads(outbound.content)
    assert set(body) == {"model", "messages", "stream", "format", "keep_alive"}
    assert body["model"] == MODEL_ID
    assert body["stream"] is False
    assert body["keep_alive"] == "5m"
    assert body["format"] == SCHEMA
    assert body["messages"] == [
        {
            "role": "user",
            "content": 'Classify the input.\n\nInput JSON:\n{"a":{"é":true},"z":1}',
        }
    ]
    assert not body["messages"][0]["content"].endswith("\n")
    assert "options" not in body


def test_schema_ref_is_resolved_and_output_is_independently_validated() -> None:
    events: list[object] = []

    def resolver(ref: str) -> Mapping[str, object]:
        events.append(("resolve", ref))
        return SCHEMA

    def validator(ref: str, value: Mapping[str, object]) -> None:
        events.append(("validate", ref, dict(value)))

    provider, _ = make_provider(resolver=resolver, validator=validator)
    assert run_infer(provider).success
    assert events == [
        ("resolve", "classification_v1"),
        (
            "validate",
            "classification_v1",
            {"category": "normal", "confidence": 0.95},
        ),
    ]


def test_schema_resolution_failure_is_invalid_and_performs_no_http() -> None:
    http_calls = 0

    def resolver(ref: str) -> Mapping[str, object]:
        raise LookupError(ref)

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal http_calls
        http_calls += 1
        return valid_response(request)

    provider, _ = make_provider(handler, resolver=resolver)
    result = run_infer(provider)
    assert result.failure_code is FailureCode.INVALID_REQUEST
    assert http_calls == 0


def test_validator_failure_is_malformed_without_output_repair() -> None:
    seen: list[Mapping[str, object]] = []

    def validator(ref: str, value: Mapping[str, object]) -> None:
        seen.append(value)
        raise ValueError("confidence must be at most one")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            json={
                "model": MODEL_ID,
                "done": True,
                "message": {"content": '{"category":"normal","confidence":100}'},
            },
        )

    provider, _ = make_provider(handler, validator=validator)
    result = run_infer(provider)
    assert result.failure_code is FailureCode.MALFORMED_OUTPUT
    assert result.structured_output is None
    assert seen[0]["confidence"] == 100


@pytest.mark.parametrize(("request_timeout", "expected_seconds"), [(1, 0.001), (300_000, 120.0)])
def test_effective_timeout_uses_minimum_rule(
    request_timeout: int, expected_seconds: float
) -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return valid_response(request)

    provider, _ = make_provider(handler)
    assert run_infer(provider, make_request(timeout_ms=request_timeout)).success
    timeout = captured[0].extensions["timeout"]
    assert timeout == {
        "connect": expected_seconds,
        "read": expected_seconds,
        "write": expected_seconds,
        "pool": expected_seconds,
    }


def test_success_result_has_exact_contract_metadata_and_no_raw_response() -> None:
    provider, _ = make_provider()
    result = run_infer(provider)
    assert result.schema_version == 1
    assert result.correlation_id == "correlation-1"
    assert result.request_id == "request-1"
    assert result.success is True
    assert result.failure_code is None
    assert result.to_dict()["structured_output"] == {
        "category": "normal",
        "confidence": 0.95,
    }
    assert result.provider_id == "ollama-local"
    assert result.model_id == MODEL_ID
    assert 0 <= result.duration_ms <= 300_000
    assert result.failure_detail is None
    assert result.warnings == ()
    assert "response" not in result.to_dict()


def test_connect_failure_maps_to_runtime_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    provider, _ = make_provider(handler)
    result = run_infer(provider)
    assert result.failure_code is FailureCode.RUNTIME_UNAVAILABLE
    assert result.structured_output is None


def test_timeout_maps_to_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    provider, _ = make_provider(handler)
    assert run_infer(provider).failure_code is FailureCode.TIMEOUT


def test_http_failure_maps_to_provider_failure_without_retry() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, request=request, text="private provider error")

    provider, _ = make_provider(handler)
    result = run_infer(provider)
    assert result.failure_code is FailureCode.PROVIDER_FAILURE
    assert result.failure_detail == "provider request failed"
    assert calls == 1


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (b"not json", FailureCode.MALFORMED_OUTPUT),
        ([], FailureCode.MALFORMED_OUTPUT),
        ({"model": MODEL_ID, "done": True}, FailureCode.MALFORMED_OUTPUT),
        (
            {"model": MODEL_ID, "done": True, "message": {}},
            FailureCode.MALFORMED_OUTPUT,
        ),
        (
            {"model": MODEL_ID, "done": True, "message": {"content": "{"}},
            FailureCode.MALFORMED_OUTPUT,
        ),
        (
            {"model": MODEL_ID, "done": True, "message": {"content": "[]"}},
            FailureCode.MALFORMED_OUTPUT,
        ),
        (
            {"model": "other", "done": True, "message": {"content": "{}"}},
            FailureCode.PROVIDER_FAILURE,
        ),
        (
            {"model": MODEL_ID, "done": False, "message": {"content": "{}"}},
            FailureCode.PROVIDER_FAILURE,
        ),
    ],
)
def test_malformed_and_incomplete_responses_map_narrowly(
    payload: object, expected: FailureCode
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if isinstance(payload, bytes):
            return httpx.Response(200, request=request, content=payload)
        return httpx.Response(200, request=request, json=payload)

    provider, _ = make_provider(handler)
    assert run_infer(provider).failure_code is expected


def test_oversized_response_is_malformed_and_contained() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, content=b"x" * 1_048_577)

    provider, _ = make_provider(handler)
    assert run_infer(provider).failure_code is FailureCode.MALFORMED_OUTPUT


@pytest.mark.parametrize(
    "content",
    ['{"value":NaN}', '{"items":' + "[0," * 17 + "0" + "]" * 17 + "}"],
)
def test_non_finite_or_contract_invalid_output_is_contained(content: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            json={
                "model": MODEL_ID,
                "done": True,
                "message": {"content": content},
            },
        )

    provider, _ = make_provider(handler)
    assert run_infer(provider).failure_code is FailureCode.MALFORMED_OUTPUT


def test_caller_cancellation_propagates_without_retry() -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise asyncio.CancelledError

    provider, _ = make_provider(handler)
    with pytest.raises(asyncio.CancelledError):
        run_infer(provider)
    assert calls == 1


def test_provider_is_async_independently_constructible_and_has_no_logger() -> None:
    provider, _ = make_provider()
    assert inspect.iscoroutinefunction(provider.infer)
    assert set(provider.__dict__) == {
        "_config",
        "_client",
        "_schema_resolver",
        "_schema_validator",
        "_descriptor",
    }
    assert not hasattr(provider, "logger")


def test_module_import_and_prohibited_source_boundaries() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert imports == {
        "__future__",
        "asyncio",
        "collections.abc",
        "dataclasses",
        "httpx",
        "ipaddress",
        "json",
        "time",
        "types",
        "urllib.parse",
        "inference_contracts",
        "provider",
    }
    prohibited = (
        "core.aios_core",
        "core.registry",
        "core.event",
        "telegram",
        "subprocess",
        "requests",
        "ollama import",
        "openai",
        "anthropic",
        "database",
        "session",
        "conversation",
        "model pull",
        "/api/version",
    )
    lowered = source.lower()
    assert not any(marker in lowered for marker in prohibited)


def test_core_has_no_reverse_adapter_dependency() -> None:
    offenders: list[str] = []
    for path in (ROOT / "core").rglob("*.py"):
        if path == MODULE_PATH or path == MODULE_PATH.parent / "__init__.py":
            continue
        source = path.read_text(encoding="utf-8")
        if "core.brain.providers" in source:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
