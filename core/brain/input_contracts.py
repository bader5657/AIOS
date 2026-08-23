"""Immutable semantic input contract for the AIOS Brain boundary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import json
import math
from types import MappingProxyType


BRAIN_INPUT_SCHEMA_VERSION = 1
MAX_IDENTIFIER_LENGTH = 128
MAX_REFERENCE_LENGTH = 512
MAX_CONTEXT_REFERENCES = 32
MAX_JSON_DEPTH = 16
MAX_JSON_MEMBERS = 256
MAX_JSON_BYTES = 1_048_576


class BrainIntent(str, Enum):
    """Approved semantic operations at the Brain receiving boundary."""

    STRUCTURED_INFERENCE = "structured_inference"


def _validate_schema_version(value: object) -> None:
    if type(value) is not int:
        raise TypeError("schema_version must be an integer")
    if value != BRAIN_INPUT_SCHEMA_VERSION:
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


def _immutable_json_value(value: object, *, depth: int) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("JSON values must not contain NaN or infinity")
        return value
    if isinstance(value, Mapping):
        if depth > MAX_JSON_DEPTH:
            raise ValueError("JSON container nesting exceeds 16 levels")
        if len(value) > MAX_JSON_MEMBERS:
            raise ValueError("JSON mapping exceeds 256 direct members")
        snapshot: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON mapping keys must be strings")
            snapshot[key] = _immutable_json_value(item, depth=depth + 1)
        return MappingProxyType(snapshot)
    if type(value) in (list, tuple):
        if depth > MAX_JSON_DEPTH:
            raise ValueError("JSON container nesting exceeds 16 levels")
        if len(value) > MAX_JSON_MEMBERS:
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
    encoded = json.dumps(
        _plain_json_value(snapshot),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(encoded) > MAX_JSON_BYTES:
        raise ValueError(f"{name} exceeds {MAX_JSON_BYTES} UTF-8 JSON bytes")
    return snapshot  # type: ignore[return-value]


def _immutable_context_references(value: object) -> tuple[str, ...]:
    if type(value) not in (list, tuple):
        raise TypeError("context_references must be a list or tuple")
    if len(value) > MAX_CONTEXT_REFERENCES:
        raise ValueError("context_references exceeds 32 values")
    result: list[str] = []
    for index, item in enumerate(value):
        _validate_bounded_string(
            f"context_references[{index}]", item, MAX_REFERENCE_LENGTH
        )
        result.append(item)
    return tuple(result)


@dataclass(frozen=True, slots=True)
class BrainInput:
    """One bounded immutable semantic request for the Brain boundary."""

    schema_version: int
    correlation_id: str
    request_id: str
    intent: BrainIntent
    data: Mapping[str, object]
    input_reference: str | None = None
    context_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_schema_version(self.schema_version)
        _validate_bounded_string(
            "correlation_id", self.correlation_id, MAX_IDENTIFIER_LENGTH
        )
        _validate_bounded_string("request_id", self.request_id, MAX_IDENTIFIER_LENGTH)
        if not isinstance(self.intent, BrainIntent):
            raise TypeError("intent must be a BrainIntent")
        if self.intent is not BrainIntent.STRUCTURED_INFERENCE:
            raise ValueError("unsupported Brain intent")
        object.__setattr__(self, "data", _immutable_json_mapping("data", self.data))
        _validate_bounded_string(
            "input_reference",
            self.input_reference,
            MAX_REFERENCE_LENGTH,
            optional=True,
        )
        object.__setattr__(
            self,
            "context_references",
            _immutable_context_references(self.context_references),
        )
