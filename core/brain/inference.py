"""Minimal provider-neutral inference invocation seam owned by AIOS Brain."""

from __future__ import annotations

from collections.abc import Mapping

from .inference_contracts import (
    SCHEMA_VERSION,
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
)
from .provider import InferenceProvider


class BrainInferenceInvoker:
    """Construct and execute exactly one bounded Brain inference request."""

    def __init__(self, provider: InferenceProvider) -> None:
        if not isinstance(provider, InferenceProvider):
            raise TypeError("provider must be an InferenceProvider")
        self._provider = provider

    async def invoke(
        self,
        *,
        correlation_id: str,
        request_id: str,
        instruction: str,
        data: Mapping[str, object],
        timeout_ms: int,
        output_schema_ref: str,
        input_reference: str | None = None,
        context_references: tuple[str, ...] = (),
    ) -> InferenceResult:
        """Invoke the configured provider once and return its result unchanged."""

        request = InferenceRequest(
            schema_version=SCHEMA_VERSION,
            correlation_id=correlation_id,
            request_id=request_id,
            capability=InferenceCapability.STRUCTURED_INFERENCE,
            input_payload={"instruction": instruction, "data": data},
            timeout_ms=timeout_ms,
            output_schema_ref=output_schema_ref,
            input_reference=input_reference,
            context_references=context_references,
        )
        return await self._provider.infer(request)
