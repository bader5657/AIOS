from __future__ import annotations

import ast
import asyncio
from collections.abc import Mapping
import inspect
from pathlib import Path

import pytest

from core.brain.inference import BrainInferenceInvoker
from core.brain.inference_contracts import (
    SCHEMA_VERSION,
    FailureCode,
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
)
from core.brain.provider import (
    InferenceProvider,
    ProviderDescriptor,
    ProviderRuntimeKind,
)


ROOT = Path(__file__).resolve().parents[3]
INFERENCE_PATH = ROOT / "core" / "brain" / "inference.py"


def make_result(
    *, failure_code: FailureCode | None = None
) -> InferenceResult:
    success = failure_code is None
    return InferenceResult(
        schema_version=SCHEMA_VERSION,
        correlation_id="correlation-1",
        request_id="request-1",
        success=success,
        failure_code=failure_code,
        structured_output={"category": "normal", "confidence": 0.9}
        if success
        else None,
        provider_id="fake-provider",
        model_id="fake-model",
        duration_ms=7,
        failure_detail=None if success else "bounded failure",
        warnings=(),
    )


class FakeProvider(InferenceProvider):
    def __init__(
        self,
        result: InferenceResult,
        *,
        error: BaseException | None = None,
    ) -> None:
        self._result = result
        self._error = error
        self.requests: list[InferenceRequest] = []
        self.infer_calls = 0
        self._descriptor = ProviderDescriptor(
            provider_id="fake-provider",
            model_id="fake-model",
            runtime_kind=ProviderRuntimeKind.LOCAL,
            capabilities=(InferenceCapability.STRUCTURED_INFERENCE,),
        )

    @property
    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        self.infer_calls += 1
        self.requests.append(request)
        if self._error is not None:
            raise self._error
        return self._result


def invocation_values() -> dict[str, object]:
    return {
        "correlation_id": "correlation-1",
        "request_id": "request-1",
        "instruction": "Classify this synthetic reading.",
        "data": {"reading": 17, "nested": {"values": [1, 2]}},
        "timeout_ms": 30_000,
        "output_schema_ref": "sensor_classification_v1",
        "input_reference": "synthetic-input-1",
        "context_references": ("context-1", "context-2"),
    }


def test_invoker_constructs_exact_request_and_invokes_provider_once() -> None:
    provider_result = make_result()
    provider = FakeProvider(provider_result)
    invoker = BrainInferenceInvoker(provider)
    values = invocation_values()

    returned = asyncio.run(invoker.invoke(**values))  # type: ignore[arg-type]

    assert returned is provider_result
    assert provider.infer_calls == 1
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert isinstance(request, InferenceRequest)
    assert request.schema_version == SCHEMA_VERSION
    assert request.capability is InferenceCapability.STRUCTURED_INFERENCE
    assert request.correlation_id == values["correlation_id"]
    assert request.request_id == values["request_id"]
    assert set(request.input_payload) == {"instruction", "data"}
    assert request.input_payload["instruction"] == values["instruction"]
    assert request.to_dict()["input_payload"]["data"] == values["data"]  # type: ignore[index]
    assert request.timeout_ms == values["timeout_ms"]
    assert request.output_schema_ref == values["output_schema_ref"]
    assert request.input_reference == values["input_reference"]
    assert request.context_references == values["context_references"]
    assert returned.provider_id == "fake-provider"
    assert returned.model_id == "fake-model"
    assert returned.structured_output == {
        "category": "normal",
        "confidence": 0.9,
    }


def test_optional_references_use_contract_defaults() -> None:
    provider = FakeProvider(make_result())
    invoker = BrainInferenceInvoker(provider)
    values = invocation_values()
    values.pop("input_reference")
    values.pop("context_references")

    asyncio.run(invoker.invoke(**values))  # type: ignore[arg-type]

    request = provider.requests[0]
    assert request.input_reference is None
    assert request.context_references == ()


def test_invalid_provider_is_rejected() -> None:
    with pytest.raises(TypeError, match="provider must be an InferenceProvider"):
        BrainInferenceInvoker(object())  # type: ignore[arg-type]


@pytest.mark.parametrize("failure_code", list(FailureCode))
def test_failure_results_pass_through_unchanged_without_retry(
    failure_code: FailureCode,
) -> None:
    provider_result = make_result(failure_code=failure_code)
    provider = FakeProvider(provider_result)
    invoker = BrainInferenceInvoker(provider)

    returned = asyncio.run(invoker.invoke(**invocation_values()))  # type: ignore[arg-type]

    assert returned is provider_result
    assert returned.failure_code is failure_code
    assert provider.infer_calls == 1


@pytest.mark.parametrize(
    ("override", "error_type"),
    [
        ({"correlation_id": ""}, ValueError),
        ({"request_id": ""}, ValueError),
        ({"instruction": object()}, TypeError),
        ({"timeout_ms": 0}, ValueError),
        ({"output_schema_ref": ""}, ValueError),
    ],
)
def test_request_contract_errors_propagate_before_provider_call(
    override: dict[str, object], error_type: type[Exception]
) -> None:
    provider = FakeProvider(make_result())
    invoker = BrainInferenceInvoker(provider)
    values = invocation_values()
    values.update(override)

    with pytest.raises(error_type):
        asyncio.run(invoker.invoke(**values))  # type: ignore[arg-type]

    assert provider.infer_calls == 0
    assert provider.requests == []


def test_unexpected_provider_exception_propagates_without_retry() -> None:
    error = RuntimeError("unexpected provider bug")
    provider = FakeProvider(make_result(), error=error)
    invoker = BrainInferenceInvoker(provider)

    with pytest.raises(RuntimeError) as captured:
        asyncio.run(invoker.invoke(**invocation_values()))  # type: ignore[arg-type]

    assert captured.value is error
    assert provider.infer_calls == 1


def test_cancellation_propagates_without_retry() -> None:
    cancellation = asyncio.CancelledError()
    provider = FakeProvider(make_result(), error=cancellation)
    invoker = BrainInferenceInvoker(provider)

    with pytest.raises(asyncio.CancelledError) as captured:
        asyncio.run(invoker.invoke(**invocation_values()))  # type: ignore[arg-type]

    assert captured.value is cancellation
    assert provider.infer_calls == 1


def test_invoke_is_async_and_has_no_version_capability_or_payload_override() -> None:
    signature = inspect.signature(BrainInferenceInvoker.invoke)
    assert inspect.iscoroutinefunction(BrainInferenceInvoker.invoke)
    assert list(signature.parameters) == [
        "self",
        "correlation_id",
        "request_id",
        "instruction",
        "data",
        "timeout_ms",
        "output_schema_ref",
        "input_reference",
        "context_references",
    ]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for name, parameter in signature.parameters.items()
        if name != "self"
    )
    assert "schema_version" not in signature.parameters
    assert "capability" not in signature.parameters
    assert "input_payload" not in signature.parameters


def test_module_has_only_approved_import_dependencies() -> None:
    tree = ast.parse(INFERENCE_PATH.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")

    assert imported_modules == {
        "__future__",
        "collections.abc",
        "inference_contracts",
        "provider",
    }


def test_module_has_no_hidden_boundary_behaviors() -> None:
    source = INFERENCE_PATH.read_text(encoding="utf-8")
    prohibited = (
        "Ollama",
        "httpx",
        "CoreRouteResult",
        "EventEnvelope",
        "Memory",
        "Specialist",
        "core.domain",
        "logging",
        "os.environ",
        "getenv",
        "registry",
        "fallback",
        "retry",
        "persist",
        "container",
        "network",
    )
    assert all(term not in source for term in prohibited)


def test_module_defines_only_the_approved_public_class() -> None:
    tree = ast.parse(INFERENCE_PATH.read_text(encoding="utf-8"))
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    assert [node.name for node in classes] == ["BrainInferenceInvoker"]
    methods = [
        node.name for node in classes[0].body if isinstance(node, ast.FunctionDef)
    ]
    assert methods == ["__init__"]
    async_methods = [
        node.name
        for node in classes[0].body
        if isinstance(node, ast.AsyncFunctionDef)
    ]
    assert async_methods == ["invoke"]


def test_fake_provider_records_provider_neutral_requests() -> None:
    provider = FakeProvider(make_result())
    assert isinstance(provider, InferenceProvider)
    assert provider.descriptor.provider_id == "fake-provider"
    assert provider.descriptor.capabilities == (
        InferenceCapability.STRUCTURED_INFERENCE,
    )
    assert provider.requests == []
    assert provider.infer_calls == 0


def test_data_annotation_is_provider_neutral_mapping() -> None:
    annotation = inspect.signature(BrainInferenceInvoker.invoke).parameters[
        "data"
    ].annotation
    assert annotation == "Mapping[str, object]"
