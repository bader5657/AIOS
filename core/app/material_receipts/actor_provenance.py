"""Candidate-only creator authorization for Stage 0.33A."""

from __future__ import annotations

from uuid import RFC_4122, UUID

from .results import ReviewApplicationError, ReviewFailureCode

def authorize_candidate_creation_actor_reference(actor_reference: str) -> str:
    """Authorize one already generically validated, immutable actor reference."""
    prefix, separator, suffix = actor_reference.partition(":")
    if separator != ":" or prefix != "operator":
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_UNAUTHORIZED)
    try:
        identifier = UUID(suffix)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_UNAUTHORIZED) from None
    if identifier.version != 4 or identifier.variant != RFC_4122 or str(identifier) != suffix:
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_UNAUTHORIZED)
    return actor_reference
