from __future__ import annotations

import asyncio
from collections.abc import Iterator
import uuid

import pytest

from core.aios_core.core import (
    CoreRouteFailureCode,
    CoreRouteResult,
    CoreRouteTarget,
)
from core.brain.inference import BrainInferenceInvoker
from core.brain.inference_contracts import (
    SCHEMA_VERSION,
    FailureCode,
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
)
from core.brain.input_contracts import (
    BRAIN_INPUT_SCHEMA_VERSION,
    BrainInput,
    BrainIntent,
)
from core.brain.provider import (
    InferenceProvider,
    ProviderDescriptor,
    ProviderRuntimeKind,
)
from core.brain.receiver import BrainSemanticReceiver
from core.core_to_brain_mapper import CoreToBrainMapper


CORRELATION_ID = "stage-0.15-correlation-1"
FIXED_UUID = uuid.UUID("01234567-89ab-4def-8123-456789abcdef")
EXPECTED_REQUEST_ID = "brain-0123456789ab4def8123456789abcdef"
INPUT_REFERENCE = "stage-0.15-synthetic-input-1"
CONTEXT_REFERENCES = (
    "stage-0.15-context-1",
    "stage-0.15-context-2",
)
INSTRUCTION = (
    "Analyze the provided data and return one concise result string in the "
    "required structured output."
)
OUTPUT_SCHEMA_REF = "brain_structured_inference_result_v1"
ORIGINAL_DATA = {
    "temperature_c": 25.0,
    "vibration": 0.12,
    "status": "stable",
}


class RecordingUuidFactory:
    def __init__(self, values: Iterator[uuid.UUID]) -> None:
        self._values = values
        self.call_count = 0

    def __call__(self) -> uuid.UUID:
        self.call_count += 1
        return next(self._values)


class FakeInferenceProvider(InferenceProvider):
    def __init__(self, result: InferenceResult) -> None:
        self._result = result
        self._descriptor = ProviderDescriptor(
            provider_id="stage-0.15-fake-provider",
            model_id="stage-0.15-fake-model",
            runtime_kind=ProviderRuntimeKind.LOCAL,
            capabilities=(InferenceCapability.STRUCTURED_INFERENCE,),
        )
        self.received: list[InferenceRequest] = []
        self.infer_call_count = 0

    @property
    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        self.infer_call_count += 1
        self.received.append(request)
        return self._result


def eligible_route_result() -> CoreRouteResult:
    return CoreRouteResult(
        success=True,
        route_target=CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
        failure_code=None,
        failure_reason=None,
    )


def map_brain_input(
    mapper: CoreToBrainMapper,
    source_data: dict[str, object],
) -> BrainInput:
    return mapper.map(
        route_result=eligible_route_result(),
        correlation_id=CORRELATION_ID,
        data=source_data,
        input_reference=INPUT_REFERENCE,
        context_references=CONTEXT_REFERENCES,
    )


def assert_brain_input(brain_input: BrainInput) -> None:
    assert type(brain_input) is BrainInput
    assert brain_input.schema_version == BRAIN_INPUT_SCHEMA_VERSION
    assert brain_input.correlation_id == CORRELATION_ID
    assert brain_input.request_id == EXPECTED_REQUEST_ID
    assert brain_input.intent is BrainIntent.STRUCTURED_INFERENCE
    assert dict(brain_input.data) == ORIGINAL_DATA
    assert brain_input.input_reference == INPUT_REFERENCE
    assert brain_input.context_references == CONTEXT_REFERENCES
    assert all(
        field not in brain_input.data
        for field in ("route_result", "route_target", "failure_code", "failure_reason")
    )


def assert_inference_request(request: InferenceRequest) -> None:
    assert type(request) is InferenceRequest
    assert request.schema_version == SCHEMA_VERSION
    assert request.correlation_id == CORRELATION_ID
    assert request.request_id == EXPECTED_REQUEST_ID
    assert request.capability is InferenceCapability.STRUCTURED_INFERENCE
    assert set(request.input_payload) == {"instruction", "data"}
    assert request.input_payload["instruction"] == INSTRUCTION
    assert dict(request.input_payload["data"]) == ORIGINAL_DATA  # type: ignore[arg-type]
    assert request.timeout_ms == 120_000
    assert request.output_schema_ref == OUTPUT_SCHEMA_REF
    assert request.input_reference == INPUT_REFERENCE
    assert request.context_references == CONTEXT_REFERENCES


def test_success_chain_preserves_snapshot_policy_request_and_result_identity() -> None:
    assert FIXED_UUID.version == 4
    uuid_factory = RecordingUuidFactory(iter((FIXED_UUID,)))
    source_data = dict(ORIGINAL_DATA)
    brain_input = map_brain_input(CoreToBrainMapper(uuid_factory), source_data)
    assert_brain_input(brain_input)

    source_data["temperature_c"] = 999.0
    source_data["status"] = "mutated"
    assert dict(brain_input.data) == ORIGINAL_DATA

    expected_result = InferenceResult(
        schema_version=SCHEMA_VERSION,
        correlation_id=brain_input.correlation_id,
        request_id=brain_input.request_id,
        success=True,
        failure_code=None,
        structured_output={"result": "normal"},
        provider_id="stage-0.15-fake-provider",
        model_id="stage-0.15-fake-model",
        duration_ms=1,
    )
    provider = FakeInferenceProvider(expected_result)
    receiver = BrainSemanticReceiver(BrainInferenceInvoker(provider))

    returned = asyncio.run(receiver.receive(brain_input))

    assert returned is expected_result
    assert uuid_factory.call_count == 1
    assert provider.infer_call_count == 1
    assert len(provider.received) == 1
    assert_inference_request(provider.received[0])


def test_timeout_result_passes_unchanged_without_retry() -> None:
    uuid_factory = RecordingUuidFactory(iter((FIXED_UUID,)))
    brain_input = map_brain_input(
        CoreToBrainMapper(uuid_factory),
        dict(ORIGINAL_DATA),
    )
    expected_failure = InferenceResult(
        schema_version=SCHEMA_VERSION,
        correlation_id=brain_input.correlation_id,
        request_id=brain_input.request_id,
        success=False,
        failure_code=FailureCode.TIMEOUT,
        structured_output=None,
        provider_id="stage-0.15-fake-provider",
        model_id="stage-0.15-fake-model",
        duration_ms=120_000,
        failure_detail="synthetic timeout",
    )
    provider = FakeInferenceProvider(expected_failure)
    receiver = BrainSemanticReceiver(BrainInferenceInvoker(provider))

    returned = asyncio.run(receiver.receive(brain_input))

    assert returned is expected_failure
    assert uuid_factory.call_count == 1
    assert provider.infer_call_count == 1
    assert len(provider.received) == 1
    assert_inference_request(provider.received[0])


def test_ineligible_core_route_fails_before_uuid_or_provider_activity() -> None:
    uuid_factory = RecordingUuidFactory(iter((FIXED_UUID,)))
    mapper = CoreToBrainMapper(uuid_factory)
    unused_result = InferenceResult(
        schema_version=SCHEMA_VERSION,
        correlation_id=CORRELATION_ID,
        request_id=EXPECTED_REQUEST_ID,
        success=False,
        failure_code=FailureCode.TIMEOUT,
        structured_output=None,
        provider_id="stage-0.15-fake-provider",
        model_id="stage-0.15-fake-model",
        duration_ms=0,
    )
    provider = FakeInferenceProvider(unused_result)
    ineligible = CoreRouteResult(
        success=False,
        route_target=None,
        failure_code=CoreRouteFailureCode.INVALID_INPUT,
        failure_reason="synthetic invalid route",
    )

    with pytest.raises(ValueError, match="not eligible"):
        mapper.map(
            route_result=ineligible,
            correlation_id=CORRELATION_ID,
            data=dict(ORIGINAL_DATA),
            input_reference=INPUT_REFERENCE,
            context_references=CONTEXT_REFERENCES,
        )

    assert uuid_factory.call_count == 0
    assert provider.infer_call_count == 0
    assert provider.received == []
