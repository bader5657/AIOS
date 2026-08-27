"""Create-only Stage 0.31B ingestion-to-review-candidate composition.

Source-level idempotency is intentionally absent before activation. Production
activation remains unauthorized until separately governed deduplication and
actor-provenance gates are closed.
"""

from __future__ import annotations

from typing import Protocol

from core.ingestion.universal_ingestion import IngestionResult

from core.material_receipts.models import (
    ReceiptCandidateRequest,
    ReceiptForReview,
    ReceiptStatus,
)

from .candidate_input import TrustedReceiptFacts, build_receipt_candidate_request
from .results import ReviewApplicationError, ReviewFailureCode
from .review_use_cases import SourceContext


__all__ = ("create_review_candidate_from_ingestion",)


class _CreateCandidateCapability(Protocol):
    """The complete authority visible to the Stage 0.31B use case."""

    async def create_candidate(
        self,
        request: ReceiptCandidateRequest,
        source_context: SourceContext,
    ) -> ReceiptForReview: ...


class _TerminalCreateCandidateCapability:
    """Stateless terminal adapter that retains no candidate runtime graph."""

    __slots__ = ()

    async def create_candidate(
        self,
        request: ReceiptCandidateRequest,
        source_context: SourceContext,
    ) -> ReceiptForReview:
        from .composition import compose_review_application

        facade = compose_review_application().facade
        return await facade.create_candidate(request, source_context)


def _candidate_capability() -> _CreateCandidateCapability:
    return _TerminalCreateCandidateCapability()


def _require_review_safe_result(result: object) -> ReceiptForReview:
    try:
        valid = (
            type(result) is ReceiptForReview
            and result.status is ReceiptStatus.NEEDS_REVIEW
            and result.confirmed_version is None
            and result.confirmed_at is None
            and result.confirmation_actor_reference is None
            and all(
                item.status is ReceiptStatus.NEEDS_REVIEW for item in result.items
            )
        )
    except (AttributeError, TypeError) as exc:
        raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from exc
    if not valid:
        raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE)
    return result

async def create_review_candidate_from_ingestion(
    ingestion_result: IngestionResult,
    trusted_receipt_facts: TrustedReceiptFacts,
) -> ReceiptForReview:
    """Map verified evidence and perform exactly one candidate-create operation."""

    request = build_receipt_candidate_request(
        ingestion_result,
        trusted_receipt_facts,
    )
    try:
        source_context = SourceContext(request.source_asset_reference)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ReviewApplicationError(
            ReviewFailureCode.SOURCE_IDENTITY_INVALID
        ) from exc
    result = await _candidate_capability().create_candidate(request, source_context)
    return _require_review_safe_result(result)
