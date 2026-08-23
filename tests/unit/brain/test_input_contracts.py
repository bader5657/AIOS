"""Tests for the BrainInput semantic boundary contract."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from enum import Enum
import logging
import math
from pathlib import Path
from types import MappingProxyType

import pytest

from core.brain.input_contracts import (
    BRAIN_INPUT_SCHEMA_VERSION,
    BrainInput,
    BrainIntent,
)


MODULE_PATH = Path(__file__).parents[3] / "core" / "brain" / "input_contracts.py"


def values() -> dict[str, object]:
    return {
        "schema_version": BRAIN_INPUT_SCHEMA_VERSION,
        "correlation_id": "correlation-1",
        "request_id": "request-1",
        "intent": BrainIntent.STRUCTURED_INFERENCE,
        "data": {"value": 1},
        "input_reference": None,
        "context_references": (),
    }


def make_input(**changes: object) -> BrainInput:
    candidate = values()
    candidate.update(changes)
    return BrainInput(**candidate)  # type: ignore[arg-type]


def nested_mapping(levels: int) -> dict[str, object]:
    value: dict[str, object] = {}
    for _ in range(levels - 1):
        value = {"nested": value}
    return value


def test_shape_version_intent_and_immutability() -> None:
    contract = make_input()

    assert BRAIN_INPUT_SCHEMA_VERSION == 1
    assert list(BrainIntent) == [BrainIntent.STRUCTURED_INFERENCE]
    assert BrainIntent.__members__ == {"STRUCTURED_INFERENCE": BrainIntent.STRUCTURED_INFERENCE}
    assert [field.name for field in fields(BrainInput)] == [
        "schema_version",
        "correlation_id",
        "request_id",
        "intent",
        "data",
        "input_reference",
        "context_references",
    ]
    assert not hasattr(contract, "__dict__")
    with pytest.raises(FrozenInstanceError):
        contract.request_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("value", [True, "1", 1.0, None])
def test_schema_version_wrong_type_rejected(value: object) -> None:
    with pytest.raises(TypeError):
        make_input(schema_version=value)


def test_schema_version_wrong_value_rejected() -> None:
    with pytest.raises(ValueError):
        make_input(schema_version=2)


@pytest.mark.parametrize("name", ["correlation_id", "request_id"])
def test_valid_identifiers_are_preserved(name: str) -> None:
    contract = make_input(**{name: " exact-id "})
    assert getattr(contract, name) == " exact-id "


@pytest.mark.parametrize("name", ["correlation_id", "request_id"])
@pytest.mark.parametrize("value", ["", "   ", "x" * 129, "bad\nvalue", "bad\x7fvalue"])
def test_invalid_identifiers_rejected(name: str, value: str) -> None:
    with pytest.raises(ValueError):
        make_input(**{name: value})


@pytest.mark.parametrize("name", ["correlation_id", "request_id"])
@pytest.mark.parametrize("value", [None, 1, b"id"])
def test_identifier_wrong_types_rejected(name: str, value: object) -> None:
    with pytest.raises(TypeError):
        make_input(**{name: value})


def test_intent_accepts_only_exact_enum_member() -> None:
    assert make_input().intent is BrainIntent.STRUCTURED_INFERENCE
    with pytest.raises(TypeError):
        make_input(intent="structured_inference")
    with pytest.raises(TypeError):
        make_input(intent=object())


def test_data_mapping_empty_nested_and_sequence_snapshot() -> None:
    assert make_input(data={}).data == {}
    source = {"nested": {"items": [1, {"active": True}]}}
    contract = make_input(data=source)

    assert isinstance(contract.data, MappingProxyType)
    nested = contract.data["nested"]
    assert isinstance(nested, MappingProxyType)
    assert nested["items"][0] == 1  # type: ignore[index]
    assert type(nested["items"]) is tuple  # type: ignore[index]
    assert isinstance(nested["items"][1], MappingProxyType)  # type: ignore[index]

    source["nested"]["items"].append(2)  # type: ignore[index,union-attr]
    source["nested"]["added"] = "later"  # type: ignore[index]
    assert len(nested["items"]) == 2  # type: ignore[arg-type,index]
    assert "added" not in nested

    with pytest.raises(TypeError):
        contract.data["new"] = 1  # type: ignore[index]


@pytest.mark.parametrize("value", [None, [], "data", 1])
def test_non_mapping_data_rejected(value: object) -> None:
    with pytest.raises(TypeError):
        make_input(data=value)


@pytest.mark.parametrize(
    "value",
    [
        {1: "value"},
        {"value": math.nan},
        {"value": math.inf},
        {"value": -math.inf},
        {"value": b"bytes"},
        {"value": {1, 2}},
        {"value": object()},
        {"value": BrainIntent.STRUCTURED_INFERENCE},
    ],
)
def test_invalid_json_data_rejected(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_input(data=value)


def test_json_depth_boundary() -> None:
    make_input(data=nested_mapping(16))
    with pytest.raises(ValueError):
        make_input(data=nested_mapping(17))


def test_json_direct_member_boundary() -> None:
    make_input(data={str(index): index for index in range(256)})
    with pytest.raises(ValueError):
        make_input(data={str(index): index for index in range(257)})
    make_input(data={"values": list(range(256))})
    with pytest.raises(ValueError):
        make_input(data={"values": list(range(257))})


def test_json_encoded_size_boundary() -> None:
    make_input(data={"value": "x" * 1_048_560})
    with pytest.raises(ValueError):
        make_input(data={"value": "x" * 1_048_576})


def test_input_reference_optional_and_valid() -> None:
    assert make_input().input_reference is None
    assert make_input(input_reference=" source-1 ").input_reference == " source-1 "


@pytest.mark.parametrize("value", ["", "  ", "x" * 513, "bad\tvalue", "bad\x7fvalue"])
def test_invalid_input_reference_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        make_input(input_reference=value)


@pytest.mark.parametrize("value", [1, b"reference", object()])
def test_input_reference_wrong_type_rejected(value: object) -> None:
    with pytest.raises(TypeError):
        make_input(input_reference=value)


def test_context_references_default_list_tuple_and_immutability() -> None:
    assert make_input().context_references == ()
    source = ["one", "two"]
    contract = make_input(context_references=source)
    source.append("later")
    assert contract.context_references == ("one", "two")
    assert type(contract.context_references) is tuple
    assert make_input(context_references=("one",)).context_references == ("one",)


def test_context_reference_count_boundary() -> None:
    make_input(context_references=[f"ref-{index}" for index in range(32)])
    with pytest.raises(ValueError):
        make_input(context_references=[f"ref-{index}" for index in range(33)])


@pytest.mark.parametrize("value", ["", "  ", "x" * 513, "bad\nvalue", "bad\x7fvalue"])
def test_invalid_context_reference_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        make_input(context_references=[value])


@pytest.mark.parametrize("value", [None, "reference", {"reference"}, object()])
def test_context_container_wrong_type_rejected(value: object) -> None:
    with pytest.raises(TypeError):
        make_input(context_references=value)


def test_context_item_wrong_type_rejected() -> None:
    with pytest.raises(TypeError):
        make_input(context_references=[1])


def test_unknown_constructor_field_rejected() -> None:
    with pytest.raises(TypeError):
        make_input(unknown="value")


def test_prohibited_fields_and_serialization_methods_are_absent() -> None:
    prohibited = {
        "instruction",
        "prompt",
        "timeout_ms",
        "output_schema_ref",
        "provider_id",
        "model_id",
        "endpoint",
        "messages",
        "options",
        "tools",
        "functions",
        "memory",
        "specialist",
        "business_action",
        "event_envelope",
        "core_route_result",
    }
    assert prohibited.isdisjoint(field.name for field in fields(BrainInput))
    assert not hasattr(BrainInput, "to_dict")
    assert not hasattr(BrainInput, "from_dict")


def test_module_has_only_approved_import_dependencies() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {
        "__future__",
        "collections",
        "dataclasses",
        "enum",
        "json",
        "math",
        "types",
    }


def test_module_has_no_logging_or_persistence_behavior(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    make_input(data={"private": "content"})
    assert not caplog.records

    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    prohibited = (
        "logging",
        "logger",
        "open(",
        "write(",
        "database",
        "postgres",
        "memory",
        "specialist",
        "core.domain",
        "core.aios_core",
        "inference_contracts",
        "from .inference",
        "provider",
        "ollama",
        "httpx",
    )
    assert all(term not in source for term in prohibited)


def test_brain_intent_is_string_enum() -> None:
    assert issubclass(BrainIntent, str)
    assert issubclass(BrainIntent, Enum)
