"""Pure semantic mapping from the AIOS Core boundary to BrainInput."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import uuid

from core.aios_core.core import CoreRouteResult, CoreRouteTarget
from core.brain.input_contracts import (
    BRAIN_INPUT_SCHEMA_VERSION,
    BrainInput,
    BrainIntent,
)


class CoreToBrainMapper:
    """Construct one BrainInput from eligible Core boundary evidence."""

    __slots__ = ("_request_id_factory",)

    def __init__(
        self,
        request_id_factory: Callable[[], uuid.UUID] = uuid.uuid4,
    ) -> None:
        if not callable(request_id_factory):
            raise TypeError("request_id_factory must be callable")
        self._request_id_factory = request_id_factory

    def map(
        self,
        *,
        route_result: CoreRouteResult,
        correlation_id: str,
        data: Mapping[str, object],
        input_reference: str | None = None,
        context_references: tuple[str, ...] = (),
    ) -> BrainInput:
        """Return one immutable BrainInput for an eligible Core handoff."""
        if type(route_result) is not CoreRouteResult:
            raise TypeError("route_result must be a CoreRouteResult")
        if not (
            route_result.success is True
            and route_result.route_target is CoreRouteTarget.AIOS_BRAIN_BOUNDARY
            and route_result.failure_code is None
            and route_result.failure_reason is None
        ):
            raise ValueError("route_result is not eligible for the Brain boundary")

        generated_id = self._request_id_factory()
        if type(generated_id) is not uuid.UUID or generated_id.version != 4:
            raise ValueError("request_id_factory must return a UUIDv4")

        return BrainInput(
            schema_version=BRAIN_INPUT_SCHEMA_VERSION,
            correlation_id=correlation_id,
            request_id=f"brain-{generated_id.hex}",
            intent=BrainIntent.STRUCTURED_INFERENCE,
            data=data,
            input_reference=input_reference,
            context_references=context_references,
        )
