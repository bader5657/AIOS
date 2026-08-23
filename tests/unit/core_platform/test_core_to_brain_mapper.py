from __future__ import annotations

import ast
from collections.abc import Iterator
import inspect
import math
from pathlib import Path
from types import MappingProxyType
import uuid

import pytest

from core.aios_core.core import (
    CoreRouteFailureCode,
    CoreRouteResult,
    CoreRouteTarget,
)
from core.brain.input_contracts import (
    BRAIN_INPUT_SCHEMA_VERSION,
    BrainInput,
    BrainIntent,
)
from core.core_to_brain_mapper import CoreToBrainMapper


MAPPER_PATH = Path(__file__).resolve().parents[3] / "core/core_to_brain_mapper.py"
UUID_1 = uuid.UUID("01234567-89ab-4def-8123-456789abcdef")
UUID_2 = uuid.UUID("fedcba98-7654-4321-8fed-cba987654321")


class RecordingFactory:
    def __init__(self, values: Iterator[object] | None = None) -> None:
        self.calls = 0
        self._values = values or iter((UUID_1,))

    def __call__(self) -> object:
        self.calls += 1
        return next(self._values)


def eligible_result() -> CoreRouteResult:
    return CoreRouteResult(
        success=True,
        route_target=CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
        failure_code=None,
        failure_reason=None,
    )


def map_input(
    mapper: CoreToBrainMapper,
    **overrides: object,
) -> BrainInput:
    arguments: dict[str, object] = {
        "route_result": eligible_result(),
        "correlation_id": "Correlation-Exact-1",
        "data": {"status": "stable"},
    }
    arguments.update(overrides)
    return mapper.map(**arguments)  # type: ignore[arg-type]


def test_constructor_supports_default_and_injected_factory_without_calling_it() -> None:
    assert isinstance(CoreToBrainMapper(), CoreToBrainMapper)
    factory = RecordingFactory()
    assert isinstance(CoreToBrainMapper(factory), CoreToBrainMapper)
    assert factory.calls == 0


@pytest.mark.parametrize("factory", (None, 1, "uuid", object()))
def test_constructor_rejects_non_callable_factory(factory: object) -> None:
    with pytest.raises(TypeError, match="request_id_factory must be callable"):
        CoreToBrainMapper(factory)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "route_result",
    (
        CoreRouteResult(False, None, CoreRouteFailureCode.INVALID_INPUT, "invalid"),
        CoreRouteResult(True, None, None, None),
        CoreRouteResult(
            True,
            CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
            CoreRouteFailureCode.INVALID_INPUT,
            None,
        ),
        CoreRouteResult(
            True,
            CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
            None,
            "unexpected",
        ),
    ),
)
def test_ineligible_route_result_is_rejected_before_uuid_generation(
    route_result: CoreRouteResult,
) -> None:
    factory = RecordingFactory()
    with pytest.raises(ValueError, match="not eligible"):
        map_input(CoreToBrainMapper(factory), route_result=route_result)
    assert factory.calls == 0


@pytest.mark.parametrize("route_result", (None, object(), "route"))
def test_wrong_route_result_type_is_rejected_before_uuid_generation(
    route_result: object,
) -> None:
    factory = RecordingFactory()
    with pytest.raises(TypeError, match="route_result must be a CoreRouteResult"):
        map_input(CoreToBrainMapper(factory), route_result=route_result)
    assert factory.calls == 0


def test_eligible_mapping_preserves_identity_and_constructs_exact_brain_input() -> None:
    factory = RecordingFactory()
    result = map_input(
        CoreToBrainMapper(factory),
        correlation_id="  Mixed-CASE-ID  ",
        data={},
    )
    assert type(result) is BrainInput
    assert result.schema_version == BRAIN_INPUT_SCHEMA_VERSION
    assert result.correlation_id == "  Mixed-CASE-ID  "
    assert result.request_id == f"brain-{UUID_1.hex}"
    assert result.intent is BrainIntent.STRUCTURED_INFERENCE
    assert result.data == {}
    assert result.input_reference is None
    assert result.context_references == ()
    assert factory.calls == 1


@pytest.mark.parametrize("correlation_id", ("", " ", 3, None))
def test_invalid_correlation_id_propagates_brain_input_error(
    correlation_id: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        map_input(CoreToBrainMapper(lambda: UUID_1), correlation_id=correlation_id)


def test_distinct_eligible_attempts_generate_distinct_uuid_based_ids() -> None:
    factory = RecordingFactory(iter((UUID_1, UUID_2)))
    mapper = CoreToBrainMapper(factory)
    first = map_input(mapper)
    second = map_input(mapper)
    assert first.request_id != second.request_id
    assert (first.request_id, second.request_id) == (
        f"brain-{UUID_1.hex}",
        f"brain-{UUID_2.hex}",
    )
    assert factory.calls == 2


@pytest.mark.parametrize("generated", ("uuid", 1, None, object()))
def test_non_uuid_factory_results_are_rejected(generated: object) -> None:
    factory = RecordingFactory(iter((generated,)))
    with pytest.raises(ValueError, match="must return a UUIDv4"):
        map_input(CoreToBrainMapper(factory))
    assert factory.calls == 1


@pytest.mark.parametrize(
    "generated",
    (
        uuid.UUID("01234567-89ab-1def-8123-456789abcdef"),
        uuid.UUID("01234567-89ab-3def-8123-456789abcdef"),
        uuid.UUID("01234567-89ab-5def-8123-456789abcdef"),
    ),
)
def test_non_v4_uuid_is_rejected(generated: uuid.UUID) -> None:
    with pytest.raises(ValueError, match="must return a UUIDv4"):
        map_input(CoreToBrainMapper(lambda: generated))


def test_request_id_has_exact_bounded_lowercase_unhyphenated_format() -> None:
    request_id = map_input(CoreToBrainMapper(lambda: UUID_1)).request_id
    prefix, value = request_id[:6], request_id[6:]
    assert prefix == "brain-"
    assert value == UUID_1.hex
    assert len(value) == 32
    assert value == value.lower()
    assert "-" not in value
    assert len(request_id) <= 128


def test_public_api_excludes_request_id_intent_and_policy_arguments() -> None:
    signature = inspect.signature(CoreToBrainMapper.map)
    assert tuple(signature.parameters) == (
        "self",
        "route_result",
        "correlation_id",
        "data",
        "input_reference",
        "context_references",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for name, parameter in signature.parameters.items()
        if name != "self"
    )
    for forbidden in ("request_id", "intent", "instruction", "timeout_ms"):
        with pytest.raises(TypeError):
            map_input(
                CoreToBrainMapper(lambda: UUID_1),
                **{forbidden: "not-authorized"},
            )


def test_nested_data_and_provenance_are_preserved_as_immutable_snapshots() -> None:
    source = {"items": [{"value": 1}], "active": True}
    references = ["context-1", "context-2"]
    result = map_input(
        CoreToBrainMapper(lambda: UUID_1),
        data=source,
        input_reference="input-1",
        context_references=references,
    )
    source["items"][0]["value"] = 2  # type: ignore[index]
    references.append("context-3")
    assert isinstance(result.data, MappingProxyType)
    assert result.data["items"] == (MappingProxyType({"value": 1}),)
    assert result.input_reference == "input-1"
    assert result.context_references == ("context-1", "context-2")
    with pytest.raises(TypeError):
        result.data["new"] = True  # type: ignore[index]


@pytest.mark.parametrize(
    "data",
    (
        [],
        {"bad": object()},
        {"bad": math.nan},
        {"bad": math.inf},
    ),
)
def test_invalid_data_propagates_brain_input_validation(data: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        map_input(CoreToBrainMapper(lambda: UUID_1), data=data)


@pytest.mark.parametrize(
    "overrides",
    (
        {"input_reference": ""},
        {"input_reference": object()},
        {"context_references": ("",)},
        {"context_references": (object(),)},
    ),
)
def test_invalid_provenance_propagates_brain_input_validation(
    overrides: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        map_input(CoreToBrainMapper(lambda: UUID_1), **overrides)


def test_route_evidence_is_not_embedded_or_added_to_semantic_data() -> None:
    data = {"temperature": 25}
    result = map_input(CoreToBrainMapper(lambda: UUID_1), data=data)
    assert dict(result.data) == data
    assert all(
        key not in result.data
        for key in ("route_result", "route_target", "failure_code", "failure_reason")
    )


def test_module_imports_only_approved_contracts_and_standard_library() -> None:
    tree = ast.parse(MAPPER_PATH.read_text(encoding="utf-8"))
    imports: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.setdefault(alias.name, set()).add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.setdefault(node.module or "", set()).update(
                alias.name for alias in node.names
            )
    assert imports == {
        "__future__": {"annotations"},
        "collections.abc": {"Callable", "Mapping"},
        "uuid": {"uuid"},
        "core.aios_core.core": {"CoreRouteResult", "CoreRouteTarget"},
        "core.brain.input_contracts": {
            "BRAIN_INPUT_SCHEMA_VERSION",
            "BrainInput",
            "BrainIntent",
        },
    }


def test_module_has_no_prohibited_api_or_behavior() -> None:
    source = MAPPER_PATH.read_text(encoding="utf-8")
    prohibited = (
        "AIOSCore",
        "EventEnvelope",
        "RequestContext",
        "BrainSemanticReceiver",
        "BrainInferenceInvoker",
        "InferenceProvider",
        "Ollama",
        "httpx",
        "telegram",
        "core.event",
        "core.registry",
        "core.storage",
        "core.domain",
        "memory",
        "specialist",
        "logging",
        "open(",
        "requests",
        "socket",
        "os.environ",
        "instruction",
        "output_schema_ref",
        "timeout_ms",
        "async def",
    )
    assert all(marker not in source for marker in prohibited)


def test_mapper_has_no_downstream_or_stateful_surface() -> None:
    assert CoreToBrainMapper.__slots__ == ("_request_id_factory",)
    assert tuple(
        name
        for name, value in vars(CoreToBrainMapper).items()
        if callable(value) and not name.startswith("_")
    ) == ("map",)
    assert not inspect.iscoroutinefunction(CoreToBrainMapper.map)
