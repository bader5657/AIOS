from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path
from types import MappingProxyType

import pytest

from core.brain.inference_contracts import (
    FailureCode,
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
)


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "core" / "brain" / "inference_contracts.py"


def make_request(**overrides: object) -> InferenceRequest:
    values: dict[str, object] = {
        "schema_version": 1,
        "correlation_id": "correlation-1",
        "request_id": "request-1",
        "capability": InferenceCapability.STRUCTURED_INFERENCE,
        "input_payload": {"text": "hello", "nested": {"values": [1, True]}},
        "timeout_ms": 30_000,
        "output_schema_ref": "summary_v1",
        "input_reference": None,
        "context_references": (),
    }
    values.update(overrides)
    return InferenceRequest(**values)  # type: ignore[arg-type]


def make_success(**overrides: object) -> InferenceResult:
    values: dict[str, object] = {
        "schema_version": 1,
        "correlation_id": "correlation-1",
        "request_id": "request-1",
        "success": True,
        "failure_code": None,
        "structured_output": {"answer": {"items": [1, 2]}},
        "provider_id": "provider",
        "model_id": "model",
        "duration_ms": 15,
        "failure_detail": None,
        "warnings": (),
    }
    values.update(overrides)
    return InferenceResult(**values)  # type: ignore[arg-type]


def make_failure(**overrides: object) -> InferenceResult:
    values: dict[str, object] = {
        "schema_version": 1,
        "correlation_id": "correlation-1",
        "request_id": "request-1",
        "success": False,
        "failure_code": FailureCode.RUNTIME_UNAVAILABLE,
        "structured_output": None,
        "provider_id": None,
        "model_id": None,
        "duration_ms": 0,
        "failure_detail": None,
        "warnings": (),
    }
    values.update(overrides)
    return InferenceResult(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("factory", [make_request, make_success])
def test_contracts_are_frozen(factory: object) -> None:
    contract = factory()  # type: ignore[operator]
    with pytest.raises(FrozenInstanceError):
        contract.request_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("factory", [make_request, make_success])
def test_contracts_use_slots(factory: object) -> None:
    assert not hasattr(factory(), "__dict__")  # type: ignore[operator]


@pytest.mark.parametrize("factory", [make_request, make_success])
def test_schema_version_is_exactly_one(factory: object) -> None:
    assert factory().schema_version == 1  # type: ignore[operator]


@pytest.mark.parametrize("factory", [make_request, make_success])
@pytest.mark.parametrize("version", [True, False])
def test_boolean_schema_version_is_rejected(factory: object, version: bool) -> None:
    with pytest.raises(TypeError):
        factory(schema_version=version)  # type: ignore[operator]


@pytest.mark.parametrize("factory", [make_request, make_success])
@pytest.mark.parametrize("version", [0, 2])
def test_unsupported_schema_version_is_rejected(
    factory: object, version: int
) -> None:
    with pytest.raises(ValueError):
        factory(schema_version=version)  # type: ignore[operator]


def test_capability_enum_is_exact() -> None:
    assert [(item.name, item.value) for item in InferenceCapability] == [
        ("STRUCTURED_INFERENCE", "structured_inference")
    ]
    with pytest.raises((TypeError, ValueError)):
        make_request(capability="structured_inference")


def test_required_request_fields_have_no_defaults() -> None:
    request_fields = {field.name: field for field in fields(InferenceRequest)}
    for name in (
        "schema_version",
        "correlation_id",
        "request_id",
        "capability",
        "input_payload",
        "timeout_ms",
        "output_schema_ref",
    ):
        assert request_fields[name].default.__class__.__name__ == "_MISSING_TYPE"


def test_optional_request_fields_are_preserved() -> None:
    request = make_request(
        input_reference="document:1", context_references=["context:1"]
    )
    assert request.input_reference == "document:1"
    assert request.context_references == ("context:1",)


def test_prohibited_request_fields_are_absent() -> None:
    names = {field.name.lower() for field in fields(InferenceRequest)}
    prohibited = {
        "deadline",
        "provider_configuration_ref",
        "model_configuration_ref",
        "tools",
        "functions",
        "session",
        "persistence",
        "memory",
        "specialist",
        "business_action",
    }
    assert names.isdisjoint(prohibited)


@pytest.mark.parametrize("name", ["correlation_id", "request_id"])
@pytest.mark.parametrize("value", ["", " ", "x" * 129, "x\n"])
def test_request_identifier_bounds(name: str, value: str) -> None:
    with pytest.raises(ValueError):
        make_request(**{name: value})
    assert getattr(make_request(**{name: "x" * 128}), name) == "x" * 128


@pytest.mark.parametrize("value", ["", " ", "x" * 513, "x\x7f"])
def test_input_reference_bounds(value: str) -> None:
    with pytest.raises(ValueError):
        make_request(input_reference=value)
    assert make_request(input_reference=None).input_reference is None
    assert make_request(input_reference="x" * 512).input_reference == "x" * 512


def test_context_reference_count_bound() -> None:
    assert len(make_request(context_references=["x"] * 32).context_references) == 32
    with pytest.raises(ValueError):
        make_request(context_references=["x"] * 33)


@pytest.mark.parametrize("value", ["", " ", "x" * 513, "x\n"])
def test_context_reference_length_bound(value: str) -> None:
    with pytest.raises(ValueError):
        make_request(context_references=[value])


@pytest.mark.parametrize("value", [0, 300_001])
def test_timeout_bounds(value: int) -> None:
    with pytest.raises(ValueError):
        make_request(timeout_ms=value)
    assert make_request(timeout_ms=1).timeout_ms == 1
    assert make_request(timeout_ms=300_000).timeout_ms == 300_000


@pytest.mark.parametrize("value", ["", " ", "x" * 257, "x\n"])
def test_output_schema_ref_bounds(value: str) -> None:
    with pytest.raises(ValueError):
        make_request(output_schema_ref=value)
    assert make_request(output_schema_ref="x" * 256).output_schema_ref == "x" * 256


def test_json_compatible_input_is_accepted() -> None:
    payload = {
        "null": None,
        "bool": True,
        "integer": 3,
        "float": 1.5,
        "string": "text",
        "sequence": [1, {"nested": False}],
    }
    assert make_request(input_payload=payload).to_dict()["input_payload"] == payload


@pytest.mark.parametrize("payload", [{1: "value"}, {"value": b"bytes"}, {"x": {1}}])
def test_invalid_json_types_are_rejected(payload: object) -> None:
    with pytest.raises(TypeError):
        make_request(input_payload=payload)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_float_is_rejected(value: float) -> None:
    with pytest.raises(ValueError):
        make_request(input_payload={"value": value})


def test_maximum_container_depth_is_enforced() -> None:
    value: object = "leaf"
    for _ in range(15):
        value = [value]
    make_request(input_payload={"value": value})
    value = [value]
    with pytest.raises(ValueError):
        make_request(input_payload={"value": value})


@pytest.mark.parametrize(
    "payload",
    [{str(index): index for index in range(257)}, {"items": list(range(257))}],
)
def test_direct_container_member_bound(payload: object) -> None:
    with pytest.raises(ValueError):
        make_request(input_payload=payload)


def test_one_mib_serialized_bound() -> None:
    make_request(input_payload={"value": "x" * (1_048_576 - 20)})
    with pytest.raises(ValueError):
        make_request(input_payload={"value": "x" * 1_048_576})


def test_request_is_a_defensive_recursive_snapshot() -> None:
    nested = {"items": [{"value": 1}]}
    request = make_request(input_payload=nested, context_references=["context"])
    nested["items"][0]["value"] = 2  # type: ignore[index]
    nested["items"].append("new")  # type: ignore[union-attr]
    assert isinstance(request.input_payload, MappingProxyType)
    assert request.input_payload["items"][0]["value"] == 1  # type: ignore[index]
    assert isinstance(request.input_payload["items"], tuple)
    with pytest.raises(TypeError):
        request.input_payload["new"] = 1  # type: ignore[index]


def test_request_serialization_round_trip() -> None:
    request = make_request(
        input_reference="source", context_references=["one", "two"]
    )
    wire = request.to_dict()
    assert InferenceRequest.from_dict(wire) == request
    json.dumps(wire, allow_nan=False)
    wire["input_payload"]["text"] = "changed"  # type: ignore[index]
    assert request.input_payload["text"] == "hello"


@pytest.mark.parametrize("mutation", ["unknown", "missing"])
def test_request_wire_fields_fail_closed(mutation: str) -> None:
    wire = make_request().to_dict()
    if mutation == "unknown":
        wire["raw_provider_response"] = {}
    else:
        del wire["request_id"]
    with pytest.raises(ValueError):
        InferenceRequest.from_dict(wire)


def test_failure_code_enum_is_exact() -> None:
    assert [(item.name, item.value) for item in FailureCode] == [
        ("INVALID_REQUEST", "invalid_request"),
        ("RUNTIME_UNAVAILABLE", "runtime_unavailable"),
        ("TIMEOUT", "timeout"),
        ("PROVIDER_FAILURE", "provider_failure"),
        ("MALFORMED_OUTPUT", "malformed_output"),
        ("POLICY_DENIED", "policy_denied"),
        ("RESOURCE_LIMIT", "resource_limit"),
    ]


@pytest.mark.parametrize(
    "overrides",
    [
        {"failure_code": FailureCode.PROVIDER_FAILURE},
        {"structured_output": None},
        {"provider_id": None},
        {"model_id": None},
    ],
)
def test_success_invariant(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        make_success(**overrides)


@pytest.mark.parametrize(
    "overrides",
    [{"failure_code": None}, {"failure_code": "timeout"}, {"structured_output": {}}],
)
def test_failure_invariant(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        make_failure(**overrides)


@pytest.mark.parametrize(
    ("provider_id", "model_id"),
    [(None, None), ("provider", None), (None, "model"), ("provider", "model")],
)
def test_provider_and_model_are_independently_nullable_on_failure(
    provider_id: str | None, model_id: str | None
) -> None:
    result = make_failure(provider_id=provider_id, model_id=model_id)
    assert (result.provider_id, result.model_id) == (provider_id, model_id)


@pytest.mark.parametrize("value", [-1, 300_001])
def test_duration_bounds(value: int) -> None:
    with pytest.raises(ValueError):
        make_failure(duration_ms=value)
    assert make_failure(duration_ms=300_000).duration_ms == 300_000


@pytest.mark.parametrize("value", ["", " ", "x" * 1_025, "x\n"])
def test_failure_detail_bounds(value: str) -> None:
    with pytest.raises(ValueError):
        make_failure(failure_detail=value)
    assert make_failure(failure_detail=None).failure_detail is None
    assert make_failure(failure_detail="x" * 1_024).failure_detail == "x" * 1_024


def test_warning_count_and_format() -> None:
    assert make_failure(warnings=["bounded_warning"] * 16).warnings == (
        "bounded_warning",
    ) * 16
    with pytest.raises(ValueError):
        make_failure(warnings=["warning"] * 17)
    for invalid in ("", "UPPER", "1start", "has-hyphen", "x" * 65):
        with pytest.raises(ValueError):
            make_failure(warnings=[invalid])


def test_result_structured_output_is_immutable_snapshot() -> None:
    output = {"items": [{"value": 1}]}
    result = make_success(structured_output=output)
    output["items"][0]["value"] = 2  # type: ignore[index]
    assert isinstance(result.structured_output, MappingProxyType)
    assert result.structured_output["items"][0]["value"] == 1  # type: ignore[index,union-attr]


@pytest.mark.parametrize("factory", [make_success, make_failure])
def test_result_serialization_round_trip(factory: object) -> None:
    result = factory()  # type: ignore[operator]
    wire = result.to_dict()
    assert InferenceResult.from_dict(wire) == result
    json.dumps(wire, allow_nan=False)


@pytest.mark.parametrize("mutation", ["unknown", "missing"])
def test_result_wire_fields_fail_closed(mutation: str) -> None:
    wire = make_success().to_dict()
    if mutation == "unknown":
        wire["raw_provider_response"] = {}
    else:
        del wire["duration_ms"]
    with pytest.raises(ValueError):
        InferenceResult.from_dict(wire)


def test_malformed_output_has_only_fail_closed_representation() -> None:
    result = make_failure(failure_code=FailureCode.MALFORMED_OUTPUT)
    assert not result.success
    assert result.structured_output is None


def test_prohibited_result_fields_are_absent() -> None:
    names = {field.name.lower() for field in fields(InferenceResult)}
    prohibited_fragments = (
        "raw_provider",
        "persistence",
        "token",
        "cost",
        "tool",
        "memory",
        "specialist",
        "business",
        "completion",
    )
    assert not any(
        fragment in name for name in names for fragment in prohibited_fragments
    )


def test_contract_imports_are_provider_neutral_stdlib_only() -> None:
    tree = ast.parse(CONTRACT_PATH.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert imported_roots <= {
        "__future__",
        "collections",
        "dataclasses",
        "enum",
        "json",
        "math",
        "re",
        "types",
        "typing",
    }


def test_core_has_no_reverse_brain_dependency() -> None:
    mapper_path = ROOT / "core/core_to_brain_mapper.py"
    allowed_mapper_import = {
        ("BRAIN_INPUT_SCHEMA_VERSION", None),
        ("BrainInput", None),
        ("BrainIntent", None),
    }
    offenders: list[str] = []
    for path in (ROOT / "core").rglob("*.py"):
        if path == CONTRACT_PATH or path.parent == CONTRACT_PATH.parent:
            continue
        source = path.read_text(encoding="utf-8")
        if path == mapper_path:
            tree = ast.parse(source, filename=str(path))
            brain_imports = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                and node.module is not None
                and (
                    node.module == "core.brain"
                    or node.module.startswith("core.brain.")
                )
            ]
            assert len(brain_imports) == 1
            assert brain_imports[0].module == "core.brain.input_contracts"
            assert {
                (alias.name, alias.asname) for alias in brain_imports[0].names
            } == allowed_mapper_import
            assert not any(
                isinstance(node, ast.Import)
                and any(
                    alias.name == "core.brain"
                    or alias.name.startswith("core.brain.")
                    for alias in node.names
                )
                for node in ast.walk(tree)
            )
            assert "from .brain" not in source
            assert "from core import brain" not in source
            continue
        if (
            "core.brain" in source
            or "from .brain" in source
            or "from core import brain" in source
        ):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
