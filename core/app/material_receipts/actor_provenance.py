"""Candidate-only creator authorization for Stage 0.33A."""

from __future__ import annotations

from uuid import RFC_4122, UUID

from .results import ReviewApplicationError, ReviewFailureCode

_ACTOR_CONTEXT_TYPE: type | None = None


def _register_actor_context_type(actor_context_type: type) -> None:
    """Bind the existing generic DTO without creating a reverse import edge."""
    global _ACTOR_CONTEXT_TYPE
    if (
        actor_context_type.__module__ != "core.app.material_receipts.review_use_cases"
        or actor_context_type.__qualname__ != "ActorContext"
        or (_ACTOR_CONTEXT_TYPE is not None and _ACTOR_CONTEXT_TYPE is not actor_context_type)
    ):
        raise RuntimeError("trusted ActorContext type registration failed")
    _ACTOR_CONTEXT_TYPE = actor_context_type


def authorize_candidate_creation_actor(actor_context: object) -> str:
    """Return one canonical creator after generic and candidate validation."""
    if actor_context is None:
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_REQUIRED)
    try:
        if _ACTOR_CONTEXT_TYPE is None or type(actor_context) is not _ACTOR_CONTEXT_TYPE:
            raise ValueError("actor_context must be an exact ActorContext")
        validated = _ACTOR_CONTEXT_TYPE.validate(actor_context)
        actor_reference = validated.actor_reference
    except (AttributeError, TypeError, ValueError) as exc:
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_INVALID) from exc
    prefix, separator, suffix = actor_reference.partition(":")
    if separator != ":" or prefix != "operator":
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_UNAUTHORIZED)
    try:
        identifier = UUID(suffix)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_UNAUTHORIZED) from exc
    if identifier.version != 4 or identifier.variant != RFC_4122 or str(identifier) != suffix:
        raise ReviewApplicationError(ReviewFailureCode.ACTOR_UNAUTHORIZED)
    return actor_reference
