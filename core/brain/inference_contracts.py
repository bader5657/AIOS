"""Provider-neutral, runtime-local inference contracts owned by AIOS Brain."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from enum import Enum
import json
import math
import re
from types import MappingProxyType


SCHEMA_VERSION = 1
MAX_IDENTIFIER_LENGTH = 128
MAX_REFERENCE_LENGTH = 512
MAX_CONTEXT_REFERENCES = 32
MAX_TIMEOUT_MS = 300_000
MAX_OUTPUT_SCHEMA_REF_LENGTH = 256
MAX_DURATION_MS = 300_000
MAX_FAILURE_DETAIL_LENGTH = 1_024
MAX_WARNINGS = 16
MAX_WARNING_CODE_LENGTH = 64
MAX_CONTAINER_DEPTH = 16
MAX_CONTAINER_MEMBERS = 256
MAX_JSON_BYTES = 1_048_576

_WARNING_CODE_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")


class InferenceCapability(str, Enum):
    """Capabilities supported by the v1 inference contract."""

    STRUCTURED_INFERENCE = "structured_inference"


class FailureCode(str, Enum):
    """Provider-neutral v1 inference failure taxonomy."""

    INVALID_REQUEST = "invalid_request"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    TIMEOUT = "timeout"
    PROVIDER_FAILURE = "provider_failure"
    MALFORMED_OUTPUT = "malformed_output"
    POLICY_DENIED = "policy_denied"
    RESOURCE_LIMIT = "resource_limit"


def _validate_schema_version(value: object) -> None:
    if type(value) is not int:
        raise TypeError("schema_version must be an integer")
    if value != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {value}")


def _validate_bounded_string(
    name: str,
    value: object,
    maximum: int,
    *,
    optional: bool = False,
) -> None:
    if value is None and optional:
        return
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value or value.isspace():
        raise ValueError(f"{name} must not be blank")
    if len(value) > maximum:
        raise ValueError(f"{name} exceeds {maximum} characters")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{name} contains an ASCII control character")


def _validate_bounded_integer(
    name: str, value: object, minimum: int, maximum: int
) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")


def _immutable_json_value(value: object, *, depth: int) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("JSON values must not contain NaN or infinity")
        return value
    if isinstance(value, Mapping):
        if depth > MAX_CONTAINER_DEPTH:
            raise ValueError("JSON container nesting exceeds 16 levels")
        if len(value) > MAX_CONTAINER_MEMBERS:
            raise ValueError("JSON mapping exceeds 256 direct members")
        snapshot: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON mapping keys must be strings")
            snapshot[key] = _immutable_json_value(item, depth=depth + 1)
        return MappingProxyType(snapshot)
    if type(value) in (list, tuple):
        if depth > MAX_CONTAINER_DEPTH:
            raise ValueError("JSON container nesting exceeds 16 levels")
        if len(value) > MAX_CONTAINER_MEMBERS:
            raise ValueError("JSON sequence exceeds 256 direct members")
        return tuple(_immutable_json_value(item, depth=depth + 1) for item in value)
    raise TypeError(f"unsupported JSON value type: {type(value).__name__}")


def _plain_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _plain_json_value(item) for key, item in value.items()}
    if type(value) is tuple:
        return [_plain_json_value(item) for item in value]
    return value


def _immutable_json_mapping(name: str, value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    snapshot = _immutable_json_value(value, depth=1)
    plain = _plain_json_value(snapshot)
    encoded = json.dumps(
        plain,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(encoded) > MAX_JSON_BYTES:
        raise ValueError(f"{name} exceeds {MAX_JSON_BYTES} UTF-8 JSON bytes")
    return snapshot  # type: ignore[return-value]


def _immutable_bounded_strings(
    name: str,
    value: object,
    *,
    maximum_count: int,
    maximum_length: int,
    warning_codes: bool = False,
) -> tuple[str, ...]:
    if type(value) not in (list, tuple):
        raise TypeError(f"{name} must be a list or tuple")
    if len(value) > maximum_count:
        raise ValueError(f"{name} exceeds {maximum_count} values")
    result: list[str] = []
    for index, item in enumerate(value):
        item_name = f"{name}[{index}]"
        _validate_bounded_string(item_name, item, maximum_length)
        if warning_codes and _WARNING_CODE_PATTERN.fullmatch(item) is None:
            raise ValueError(f"{item_name} is not a valid warning code")
        result.append(item)
    return tuple(result)


def _require_wire_fields(
    value: object, expected_fields: frozenset[str]
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("wire value must be a mapping")
    if not all(isinstance(key, str) for key in value):
        raise TypeError("wire field names must be strings")
    actual_fields = frozenset(value)
    missing = expected_fields - actual_fields
    unknown = actual_fields - expected_fields
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
    return value


@dataclass(frozen=True, slots=True)
class InferenceRequest:
    """One bounded, stateless, provider-neutral inference request."""

    schema_version: int
    correlation_id: str
    request_id: str
    capability: InferenceCapability
    input_payload: Mapping[str, object]
    timeout_ms: int
    output_schema_ref: str
    input_reference: str | None = None
    context_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_schema_version(self.schema_version)
        _validate_bounded_string(
            "correlation_id", self.correlation_id, MAX_IDENTIFIER_LENGTH
        )
        _validate_bounded_string("request_id", self.request_id, MAX_IDENTIFIER_LENGTH)
        if self.capability is not InferenceCapability.STRUCTURED_INFERENCE:
            raise ValueError("unsupported inference capability")
        object.__setattr__(
            self,
            "input_payload",
            _immutable_json_mapping("input_payload", self.input_payload),
        )
        _validate_bounded_integer("timeout_ms", self.timeout_ms, 1, MAX_TIMEOUT_MS)
        _validate_bounded_string(
            "output_schema_ref",
            self.output_schema_ref,
            MAX_OUTPUT_SCHEMA_REF_LENGTH,
        )
        _validate_bounded_string(
            "input_reference",
            self.input_reference,
            MAX_REFERENCE_LENGTH,
            optional=True,
        )
        object.__setattr__(
            self,
            "context_references",
            _immutable_bounded_strings(
                "context_references",
                self.context_references,
                maximum_count=MAX_CONTEXT_REFERENCES,
                maximum_length=MAX_REFERENCE_LENGTH,
            ),
        )

    def to_dict(self) -> dict[str, object]:
        """Return a detached JSON-compatible v1 wire representation."""

        return {
            "schema_version": self.schema_version,
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "capability": self.capability.value,
            "input_payload": _plain_json_value(self.input_payload),
            "timeout_ms": self.timeout_ms,
            "output_schema_ref": self.output_schema_ref,
            "input_reference": self.input_reference,
            "context_references": list(self.context_references),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> InferenceRequest:
        """Construct a validated immutable request from its exact v1 wire form."""

        wire = _require_wire_fields(value, _request_wire_fields())
        capability_value = wire["capability"]
        if not isinstance(capability_value, str):
            raise TypeError("capability must be a string")
        try:
            capability = InferenceCapability(capability_value)
        except ValueError as error:
            raise ValueError("unsupported inference capability") from error
        return cls(
            schema_version=wire["schema_version"],  # type: ignore[arg-type]
            correlation_id=wire["correlation_id"],  # type: ignore[arg-type]
            request_id=wire["request_id"],  # type: ignore[arg-type]
            capability=capability,
            input_payload=wire["input_payload"],  # type: ignore[arg-type]
            timeout_ms=wire["timeout_ms"],  # type: ignore[arg-type]
            output_schema_ref=wire["output_schema_ref"],  # type: ignore[arg-type]
            input_reference=wire["input_reference"],  # type: ignore[arg-type]
            context_references=wire["context_references"],  # type: ignore[arg-type]
        )


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """One bounded, stateless, provider-neutral inference result."""

    schema_version: int
    correlation_id: str
    request_id: str
    success: bool
    failure_code: FailureCode | None
    structured_output: Mapping[str, object] | None
    provider_id: str | None
    model_id: str | None
    duration_ms: int
    failure_detail: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_schema_version(self.schema_version)
        _validate_bounded_string(
            "correlation_id", self.correlation_id, MAX_IDENTIFIER_LENGTH
        )
        _validate_bounded_string("request_id", self.request_id, MAX_IDENTIFIER_LENGTH)
        if type(self.success) is not bool:
            raise TypeError("success must be a boolean")
        _validate_bounded_string(
            "provider_id", self.provider_id, MAX_IDENTIFIER_LENGTH, optional=True
        )
        _validate_bounded_string(
            "model_id", self.model_id, MAX_IDENTIFIER_LENGTH, optional=True
        )
        _validate_bounded_integer(
            "duration_ms", self.duration_ms, 0, MAX_DURATION_MS
        )
        _validate_bounded_string(
            "failure_detail",
            self.failure_detail,
            MAX_FAILURE_DETAIL_LENGTH,
            optional=True,
        )
        object.__setattr__(
            self,
            "warnings",
            _immutable_bounded_strings(
                "warnings",
                self.warnings,
                maximum_count=MAX_WARNINGS,
                maximum_length=MAX_WARNING_CODE_LENGTH,
                warning_codes=True,
            ),
        )
        if self.success:
            if self.failure_code is not None:
                raise ValueError("successful result cannot have a failure_code")
            if self.structured_output is None:
                raise ValueError("successful result requires structured_output")
            if self.provider_id is None or self.model_id is None:
                raise ValueError("successful result requires provider_id and model_id")
            object.__setattr__(
                self,
                "structured_output",
                _immutable_json_mapping(
                    "structured_output", self.structured_output
                ),
            )
        else:
            if not isinstance(self.failure_code, FailureCode):
                raise ValueError("failed result requires a FailureCode")
            if self.structured_output is not None:
                raise ValueError("failed result cannot have structured_output")

    def to_dict(self) -> dict[str, object]:
        """Return a detached JSON-compatible v1 wire representation."""

        return {
            "schema_version": self.schema_version,
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "success": self.success,
            "failure_code": (
                self.failure_code.value if self.failure_code is not None else None
            ),
            "structured_output": (
                _plain_json_value(self.structured_output)
                if self.structured_output is not None
                else None
            ),
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "duration_ms": self.duration_ms,
            "failure_detail": self.failure_detail,
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> InferenceResult:
        """Construct a validated immutable result from its exact v1 wire form."""

        wire = _require_wire_fields(value, _result_wire_fields())
        failure_value = wire["failure_code"]
        if failure_value is None:
            failure_code = None
        else:
            if not isinstance(failure_value, str):
                raise TypeError("failure_code must be a string or None")
            try:
                failure_code = FailureCode(failure_value)
            except ValueError as error:
                raise ValueError("unsupported failure_code") from error
        return cls(
            schema_version=wire["schema_version"],  # type: ignore[arg-type]
            correlation_id=wire["correlation_id"],  # type: ignore[arg-type]
            request_id=wire["request_id"],  # type: ignore[arg-type]
            success=wire["success"],  # type: ignore[arg-type]
            failure_code=failure_code,
            structured_output=wire["structured_output"],  # type: ignore[arg-type]
            provider_id=wire["provider_id"],  # type: ignore[arg-type]
            model_id=wire["model_id"],  # type: ignore[arg-type]
            duration_ms=wire["duration_ms"],  # type: ignore[arg-type]
            failure_detail=wire["failure_detail"],  # type: ignore[arg-type]
            warnings=wire["warnings"],  # type: ignore[arg-type]
        )


def _request_wire_fields() -> frozenset[str]:
    return frozenset(field.name for field in fields(InferenceRequest))


def _result_wire_fields() -> frozenset[str]:
    return frozenset(field.name for field in fields(InferenceResult))
