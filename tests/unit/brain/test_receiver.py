"""Tests for the minimal Brain semantic receiver."""

from __future__ import annotations

import ast
import asyncio
from dataclasses import FrozenInstanceError, fields
import inspect
import logging
from pathlib import Path
from types import MappingProxyType

import pytest

from core.brain import receiver as receiver_module
from core.brain.inference import BrainInferenceInvoker
from core.brain.inference_contracts import (
    SCHEMA_VERSION,
    FailureCode,
    InferenceResult,
)
from core.brain.input_contracts import (
    BRAIN_INPUT_SCHEMA_VERSION,
    BrainInput,
    BrainIntent,
)
from core.brain.receiver import BrainSemanticReceiver


ROOT = Path(__file__).resolve().parents[3]
RECEIVER_PATH = ROOT / "core" / "brain" / "receiver.py"
EXPECTED_INSTRUCTION = (
    "Analyze the provided data and return one concise result string "
    "in the required structured output."
)


def make_input(
    *,
    data: dict[str, object] | None = None,
    input_reference: str | None = "input-1",
    context_references: tuple[str, ...] = ("context-1", "context-2"),
) -> BrainInput:
    return BrainInput(
        schema_version=BRAIN_INPUT_SCHEMA_VERSION,
        correlation_id="correlation-1",
        request_id="request-1",
        intent=BrainIntent.STRUCTURED_INFERENCE,
        data={"value": 7, "nested": {"active": True}} if data is None else data,
        input_reference=input_reference,
        context_references=context_references,
    )


def make_result(*, failure_code: FailureCode | None = None) -> InferenceResult:
    success = failure_code is None
    return InferenceResult(
        schema_version=SCHEMA_VERSION,
        correlation_id="correlation-1",
        request_id="request-1",
        success=success,
        failure_code=failure_code,
        structured_output={"result": "accepted"} if success else None,
        provider_id="recorded-provider",
        model_id="recorded-model",
        duration_ms=11,
        failure_detail=None if success else "bounded failure",
        warnings=(),
    )


class RecordingInvoker(BrainInferenceInvoker):
    def __init__(
        self,
        result: InferenceResult,
        *,
        error: BaseException | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def invoke(self, **kwargs: object) -> InferenceResult:  # type: ignore[override]
        self.calls.append(dict(kwargs))
        if self.error is not None:
            raise self.error
        return self.result


def test_receiver_shape_construction_and_async_signature() -> None:
    invoker = RecordingInvoker(make_result())
    receiver = BrainSemanticReceiver(invoker)
    signature = inspect.signature(BrainSemanticReceiver.receive)

    assert receiver._invoker is invoker
    assert BrainSemanticReceiver.__slots__ == ("_invoker",)
    assert inspect.iscoroutinefunction(BrainSemanticReceiver.receive)
    assert list(signature.parameters) == ["self", "brain_input"]


def test_invalid_invoker_is_rejected() -> None:
    with pytest.raises(TypeError, match="invoker must be a BrainInferenceInvoker"):
        BrainSemanticReceiver(object())  # type: ignore[arg-type]


def test_wrong_input_fails_before_invocation() -> None:
    invoker = RecordingInvoker(make_result())
    receiver = BrainSemanticReceiver(invoker)

    with pytest.raises(TypeError, match="brain_input must be a BrainInput"):
        asyncio.run(receiver.receive(object()))  # type: ignore[arg-type]

    assert invoker.calls == []


def test_exact_static_policy_is_private_frozen_and_immutable() -> None:
    assert list(receiver_module._INTENT_POLICIES) == [
        BrainIntent.STRUCTURED_INFERENCE
    ]
    policy = receiver_module._INTENT_POLICIES[
        BrainIntent.STRUCTURED_INFERENCE
    ]
    assert [field.name for field in fields(policy)] == [
        "instruction",
        "timeout_ms",
        "output_schema_ref",
    ]
    assert policy.instruction == EXPECTED_INSTRUCTION
    assert policy.timeout_ms == 120_000
    assert policy.output_schema_ref == "brain_structured_inference_result_v1"
    assert not hasattr(policy, "__dict__")
    with pytest.raises(FrozenInstanceError):
        policy.timeout_ms = 1  # type: ignore[misc]
    with pytest.raises(TypeError):
        receiver_module._INTENT_POLICIES[BrainIntent.STRUCTURED_INFERENCE] = policy  # type: ignore[index]


def test_exact_invocation_arguments_and_identity() -> None:
    result = make_result()
    invoker = RecordingInvoker(result)
    receiver = BrainSemanticReceiver(invoker)
    brain_input = make_input()

    returned = asyncio.run(receiver.receive(brain_input))

    assert returned is result
    assert len(invoker.calls) == 1
    assert invoker.calls[0] == {
        "correlation_id": brain_input.correlation_id,
        "request_id": brain_input.request_id,
        "instruction": EXPECTED_INSTRUCTION,
        "data": brain_input.data,
        "timeout_ms": 120_000,
        "output_schema_ref": "brain_structured_inference_result_v1",
        "input_reference": brain_input.input_reference,
        "context_references": brain_input.context_references,
    }
    assert invoker.calls[0]["data"] is brain_input.data
    assert returned.provider_id == "recorded-provider"
    assert returned.model_id == "recorded-model"
    assert returned.structured_output == {"result": "accepted"}


def test_default_references_are_forwarded_unchanged() -> None:
    invoker = RecordingInvoker(make_result())
    receiver = BrainSemanticReceiver(invoker)
    brain_input = make_input(input_reference=None, context_references=())

    asyncio.run(receiver.receive(brain_input))

    assert invoker.calls[0]["input_reference"] is None
    assert invoker.calls[0]["context_references"] == ()


def test_data_is_not_mutated_or_enriched() -> None:
    brain_input = make_input(data={"only": [1, 2]})
    before = repr(brain_input.data)
    invoker = RecordingInvoker(make_result())

    asyncio.run(BrainSemanticReceiver(invoker).receive(brain_input))

    assert invoker.calls[0]["data"] is brain_input.data
    assert repr(brain_input.data) == before
    assert set(brain_input.data) == {"only"}


def test_public_method_has_no_policy_or_identity_overrides() -> None:
    signature = inspect.signature(BrainSemanticReceiver.receive)
    prohibited = {
        "correlation_id",
        "request_id",
        "instruction",
        "timeout_ms",
        "output_schema_ref",
    }
    assert prohibited.isdisjoint(signature.parameters)

    invoker = RecordingInvoker(make_result())
    with pytest.raises(TypeError):
        asyncio.run(
            BrainSemanticReceiver(invoker).receive(
                make_input(), instruction="override"  # type: ignore[call-arg]
            )
        )
    assert invoker.calls == []


def test_missing_policy_fails_before_invocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invoker = RecordingInvoker(make_result())
    monkeypatch.setattr(receiver_module, "_INTENT_POLICIES", MappingProxyType({}))

    with pytest.raises(ValueError, match="unsupported Brain intent policy"):
        asyncio.run(BrainSemanticReceiver(invoker).receive(make_input()))

    assert invoker.calls == []


@pytest.mark.parametrize("failure_code", list(FailureCode))
def test_failed_results_pass_through_by_identity_without_retry(
    failure_code: FailureCode,
) -> None:
    result = make_result(failure_code=failure_code)
    invoker = RecordingInvoker(result)

    returned = asyncio.run(BrainSemanticReceiver(invoker).receive(make_input()))

    assert returned is result
    assert returned.failure_code is failure_code
    assert len(invoker.calls) == 1


def test_unexpected_exception_propagates_without_retry() -> None:
    error = RuntimeError("unexpected invoker failure")
    invoker = RecordingInvoker(make_result(), error=error)

    with pytest.raises(RuntimeError) as captured:
        asyncio.run(BrainSemanticReceiver(invoker).receive(make_input()))

    assert captured.value is error
    assert len(invoker.calls) == 1


def test_cancellation_propagates_without_retry() -> None:
    cancellation = asyncio.CancelledError()
    invoker = RecordingInvoker(make_result(), error=cancellation)

    with pytest.raises(asyncio.CancelledError) as captured:
        asyncio.run(BrainSemanticReceiver(invoker).receive(make_input()))

    assert captured.value is cancellation
    assert len(invoker.calls) == 1


def test_receiver_has_only_approved_import_dependencies() -> None:
    tree = ast.parse(RECEIVER_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    assert imports <= {
        "__future__",
        "dataclasses",
        "types",
        "inference",
        "inference_contracts",
        "input_contracts",
    }


def test_receiver_has_no_logging_persistence_or_prohibited_behavior(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG)
    asyncio.run(BrainSemanticReceiver(RecordingInvoker(make_result())).receive(make_input()))
    assert not [record for record in caplog.records if record.name == "core.brain.receiver"]

    source = RECEIVER_PATH.read_text(encoding="utf-8").lower()
    prohibited = (
        "core.aios_core",
        "core.domain",
        "eventenvelope",
        "corerouteresult",
        "inferenceprovider",
        "ollama",
        "httpx",
        "providerconfig",
        "schema_resolver",
        "schema_validator",
        "logging",
        "logger",
        "open(",
        "write(",
        "database",
        "postgres",
        "memory",
        "specialist",
        "business",
        "telegram",
        "startup",
        "systemctl",
        "docker",
    )
    assert all(term not in source for term in prohibited)


def test_receiver_contains_one_invocation_and_no_retry_or_fallback() -> None:
    tree = ast.parse(RECEIVER_PATH.read_text(encoding="utf-8"))
    invoke_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "invoke"
    ]
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

    assert len(invoke_calls) == 1
    assert "retry" not in names
    assert "fallback" not in names
    assert not any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
