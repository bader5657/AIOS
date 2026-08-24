"""Tests for the immutable Stage 0.18 structured-result schema binding."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

import pytest

from core.brain.schema_binding import resolve_schema, validate_schema


SCHEMA_REF = "brain_structured_inference_result_v1"
MODULE_PATH = Path(__file__).resolve().parents[3] / "core/brain/schema_binding.py"


def test_public_resolver_returns_exact_deterministic_schema() -> None:
    first = resolve_schema(SCHEMA_REF)
    second = resolve_schema(SCHEMA_REF)

    assert first is second
    assert isinstance(first, Mapping)
    assert set(first) == {
        "type",
        "properties",
        "required",
        "additionalProperties",
    }
    assert first["type"] == "object"
    assert first["required"] == ("result",)
    assert first["additionalProperties"] is False

    properties = first["properties"]
    assert isinstance(properties, Mapping)
    assert set(properties) == {"result"}
    assert properties["result"] == {"type": "string"}
    assert set(properties["result"]) == {"type"}


@pytest.mark.parametrize(
    "schema_ref",
    [
        "unknown",
        " brain_structured_inference_result_v1",
        "brain_structured_inference_result_v1 ",
        "BRAIN_STRUCTURED_INFERENCE_RESULT_V1",
    ],
)
def test_resolver_rejects_every_non_exact_string_reference(schema_ref: str) -> None:
    with pytest.raises(ValueError, match="unsupported schema_ref"):
        resolve_schema(schema_ref)


@pytest.mark.parametrize("schema_ref", [None, 1, b"ref", object()])
def test_resolver_rejects_non_string_references(schema_ref: object) -> None:
    with pytest.raises(TypeError, match="schema_ref must be a string"):
        resolve_schema(schema_ref)  # type: ignore[arg-type]


def test_every_authoritative_schema_layer_is_immutable() -> None:
    schema = resolve_schema(SCHEMA_REF)
    properties = schema["properties"]
    assert type(schema) is MappingProxyType
    assert type(properties) is MappingProxyType
    assert type(properties["result"]) is MappingProxyType
    assert type(schema["required"]) is tuple

    with pytest.raises(TypeError):
        schema["type"] = "array"  # type: ignore[index]
    with pytest.raises(TypeError):
        properties["other"] = {}  # type: ignore[index]
    with pytest.raises(TypeError):
        properties["result"]["type"] = "number"  # type: ignore[index]
    with pytest.raises(TypeError):
        schema["required"][0] = "other"  # type: ignore[index]

    later = resolve_schema(SCHEMA_REF)
    assert later["type"] == "object"
    assert set(later["properties"]) == {"result"}
    assert later["properties"]["result"] == {"type": "string"}
    assert later["required"] == ("result",)


def test_schema_has_no_unapproved_keywords_or_fields() -> None:
    schema = resolve_schema(SCHEMA_REF)
    result_definition = schema["properties"]["result"]

    assert set(result_definition) == {"type"}
    assert "minLength" not in result_definition
    assert "maxLength" not in result_definition
    assert "pattern" not in result_definition
    assert "description" not in result_definition
    assert "title" not in schema
    assert "provider" not in schema
    assert "model" not in schema


@pytest.mark.parametrize("result", ["normal", "", "日本語", "😀", "  exact  "])
def test_validator_accepts_exact_string_results_without_rewriting(
    result: str,
) -> None:
    value = {"result": result}
    before = value.copy()

    returned = validate_schema(SCHEMA_REF, value)

    assert returned is None
    assert value == before
    assert value["result"] == result


@pytest.mark.parametrize("value", [None, 1, 1.5, True, "result", [], ()])
def test_validator_rejects_non_mapping_values(value: object) -> None:
    with pytest.raises(TypeError, match="value must be a mapping"):
        validate_schema(SCHEMA_REF, value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"other": "value"},
        {"result": "ok", "extra": 1},
        {"result": "ok", "extra": 1, "another": 2},
    ],
)
def test_validator_rejects_missing_or_extra_fields(value: dict[str, object]) -> None:
    before = value.copy()
    with pytest.raises(ValueError, match="exactly the result field"):
        validate_schema(SCHEMA_REF, value)
    assert value == before


@pytest.mark.parametrize(
    "result",
    [None, True, 1, 1.0, [], (), {}, object()],
)
def test_validator_rejects_every_non_exact_string_result(result: object) -> None:
    value = {"result": result}
    with pytest.raises(TypeError, match="result must be a string"):
        validate_schema(SCHEMA_REF, value)
    assert value["result"] is result


@pytest.mark.parametrize(
    "schema_ref",
    [
        "unknown",
        " brain_structured_inference_result_v1",
        "brain_structured_inference_result_v1 ",
        "BRAIN_STRUCTURED_INFERENCE_RESULT_V1",
    ],
)
def test_validator_rejects_non_exact_string_references_first(
    schema_ref: str,
) -> None:
    with pytest.raises(ValueError, match="unsupported schema_ref"):
        validate_schema(schema_ref, {"result": "ok"})


@pytest.mark.parametrize("schema_ref", [None, 1, b"ref", object()])
def test_validator_rejects_non_string_references_first(schema_ref: object) -> None:
    with pytest.raises(TypeError, match="schema_ref must be a string"):
        validate_schema(schema_ref, {"result": "ok"})  # type: ignore[arg-type]


def test_production_module_is_standard_library_only_and_side_effect_free() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MODULE_PATH))
    imports = [
        node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    imported_modules = {
        node.module
        for node in imports
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert imported_modules == {"collections.abc", "types"}
    assert not [node for node in imports if isinstance(node, ast.Import)]

    prohibited = (
        "OllamaInferenceProvider",
        "OllamaProviderConfig",
        "httpx",
        "BrainSemanticReceiver",
        "BrainInferenceInvoker",
        "core.aios_core",
        "universal_ingestion",
        "telegram",
        "Registry",
        "database",
        "filesystem",
        "network",
        "environ",
        "getenv",
        "config",
        "logging",
        "logger",
        "persist",
        "Memory",
        "Specialist",
        "core.domain",
        "provider_id",
        "model_id",
    )
    for marker in prohibited:
        assert marker not in source


def test_module_exposes_only_one_supported_schema_reference() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MODULE_PATH))
    string_literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    schema_refs = [
        value for value in string_literals if value.endswith("_inference_result_v1")
    ]
    assert schema_refs == [SCHEMA_REF]


def test_public_api_has_exact_provider_compatible_signatures() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    assert set(functions) == {"resolve_schema", "validate_schema"}
    assert [argument.arg for argument in functions["resolve_schema"].args.args] == [
        "schema_ref"
    ]
    assert [argument.arg for argument in functions["validate_schema"].args.args] == [
        "schema_ref",
        "value",
    ]
    for function in functions.values():
        assert function.args.defaults == []
        assert function.args.kwonlyargs == []
        assert function.args.vararg is None
        assert function.args.kwarg is None
