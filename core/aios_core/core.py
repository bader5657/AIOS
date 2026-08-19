"""Fresh contract-first AIOS Core runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.domain.event_envelope import EventEnvelope


class CoreRouteTarget(str, Enum):
    """Approved destination boundary for a valid envelope."""

    AIOS_BRAIN_BOUNDARY = "aios_brain_boundary"


class CoreRouteFailureCode(str, Enum):
    """Approved bounded route failure."""

    INVALID_INPUT = "invalid_input"


@dataclass(frozen=True, slots=True)
class CoreRouteResult:
    """Runtime-local result of an AIOS Core route operation."""

    success: bool
    route_target: CoreRouteTarget | None
    failure_code: CoreRouteFailureCode | None
    failure_reason: str | None


class AIOSCore:
    """Stateless boundary router for immutable event envelopes."""

    __slots__ = ()

    async def route(self, envelope: EventEnvelope) -> CoreRouteResult:
        """Route a valid envelope to the sole approved boundary."""
        if not isinstance(envelope, EventEnvelope):
            return CoreRouteResult(
                success=False,
                route_target=None,
                failure_code=CoreRouteFailureCode.INVALID_INPUT,
                failure_reason="route input must be an EventEnvelope",
            )

        return CoreRouteResult(
            success=True,
            route_target=CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
            failure_code=None,
            failure_reason=None,
        )
