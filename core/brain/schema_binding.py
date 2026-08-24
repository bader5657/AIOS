"""Immutable binding for the sole approved structured-result schema."""

from collections.abc import Mapping
from types import MappingProxyType


_SCHEMA_REF = "brain_structured_inference_result_v1"
_RESULT_DEFINITION: Mapping[str, object] = MappingProxyType({"type": "string"})
_PROPERTIES: Mapping[str, object] = MappingProxyType(
    {"result": _RESULT_DEFINITION}
)
_SCHEMA: Mapping[str, object] = MappingProxyType(
    {
        "type": "object",
        "properties": _PROPERTIES,
        "required": ("result",),
        "additionalProperties": False,
    }
)


def resolve_schema(schema_ref: str) -> Mapping[str, object]:
    """Resolve the exact approved reference to its immutable schema."""
    if not isinstance(schema_ref, str):
        raise TypeError("schema_ref must be a string")
    if schema_ref != _SCHEMA_REF:
        raise ValueError("unsupported schema_ref")
    return _SCHEMA


def validate_schema(schema_ref: str, value: Mapping[str, object]) -> None:
    """Validate one parsed value against the exact approved schema."""
    resolve_schema(schema_ref)
    if not isinstance(value, Mapping):
        raise TypeError("value must be a mapping")
    if frozenset(value) != frozenset(("result",)):
        raise ValueError("value must contain exactly the result field")
    if type(value["result"]) is not str:
        raise TypeError("result must be a string")
