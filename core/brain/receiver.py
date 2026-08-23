"""Minimal semantic receiver owned by the AIOS Brain boundary."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from .inference import BrainInferenceInvoker
from .inference_contracts import InferenceResult
from .input_contracts import BrainInput, BrainIntent


@dataclass(frozen=True, slots=True)
class _IntentPolicy:
    instruction: str
    timeout_ms: int
    output_schema_ref: str


_INTENT_POLICIES = MappingProxyType(
    {
        BrainIntent.STRUCTURED_INFERENCE: _IntentPolicy(
            instruction=(
                "Analyze the provided data and return one concise result string "
                "in the required structured output."
            ),
            timeout_ms=120_000,
            output_schema_ref="brain_structured_inference_result_v1",
        )
    }
)


class BrainSemanticReceiver:
    """Translate one semantic Brain input into one bounded invocation."""

    __slots__ = ("_invoker",)

    def __init__(self, invoker: BrainInferenceInvoker) -> None:
        if not isinstance(invoker, BrainInferenceInvoker):
            raise TypeError("invoker must be a BrainInferenceInvoker")
        self._invoker = invoker

    async def receive(self, brain_input: BrainInput) -> InferenceResult:
        """Invoke the static policy for one validated Brain input."""

        if not isinstance(brain_input, BrainInput):
            raise TypeError("brain_input must be a BrainInput")
        policy = _INTENT_POLICIES.get(brain_input.intent)
        if policy is None:
            raise ValueError("unsupported Brain intent policy")

        return await self._invoker.invoke(
            correlation_id=brain_input.correlation_id,
            request_id=brain_input.request_id,
            instruction=policy.instruction,
            data=brain_input.data,
            timeout_ms=policy.timeout_ms,
            output_schema_ref=policy.output_schema_ref,
            input_reference=brain_input.input_reference,
            context_references=brain_input.context_references,
        )
