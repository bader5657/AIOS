"""Create-only Stage 0.31B ingestion-to-review-candidate composition.

Source-level idempotency is intentionally absent before activation. Production
activation remains unauthorized until separately governed deduplication and
actor-provenance gates are closed.
"""

from __future__ import annotations

from typing import Protocol

from core.ingestion.universal_ingestion import IngestionResult

from core.material_receipts.errors import MaterialReceiptFailureCode
from core.material_receipts.models import (
    ReceiptCandidateRequest,
    ReceiptForReview,
    ReceiptStatus,
)

from .candidate_input import TrustedReceiptFacts, build_receipt_candidate_request
from .candidate_input_errors import CandidateInputError, CandidateInputFailureCode
from .results import ReviewApplicationError, ReviewFailureCode
from .review_use_cases import ActorContext, SourceContext
from .actor_provenance import authorize_candidate_creation_actor_reference


__all__ = ("create_review_candidate_from_ingestion",)


class _CreateCandidateCapability(Protocol):
    """The complete authority visible to the Stage 0.31B use case."""

    async def create_candidate(
        self,
        request: ReceiptCandidateRequest,
        source_context: SourceContext,
        created_by_actor_reference: str,
    ) -> ReceiptForReview: ...


class _TerminalCreateCandidateCapability:
    """Stateless terminal adapter that retains no candidate runtime graph."""

    __slots__ = ()

    async def create_candidate(
        self,
        request: ReceiptCandidateRequest,
        source_context: SourceContext,
        created_by_actor_reference: str,
    ) -> ReceiptForReview:
        result, failure_code, candidate_code = await _execute_terminal_create(
            request,
            source_context,
            created_by_actor_reference,
        )
        if failure_code is not None:
            raise ReviewApplicationError(
                failure_code,
                candidate_code=candidate_code,
            )
        if result is None:
            raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE)
        return result


async def _execute_terminal_create(
    request: ReceiptCandidateRequest,
    source_context: SourceContext,
    created_by_actor_reference: str,
) -> tuple[
    ReceiptForReview | None,
    ReviewFailureCode | None,
    MaterialReceiptFailureCode | None,
]:
    """Quarantine the transient Stage 0.30 graph and its failure tracebacks."""

    try:
        from .composition import compose_review_application

        facade = compose_review_application().facade
        result = await facade.create_candidate(
            request, source_context, created_by_actor_reference
        )
    except ReviewApplicationError as exc:
        try:
            failure_code = exc.code
            candidate_code = exc.candidate_code
        except Exception:
            return None, ReviewFailureCode.INTERNAL_FAILURE, None
        if type(failure_code) is not ReviewFailureCode:
            return None, ReviewFailureCode.INTERNAL_FAILURE, None
        if (
            candidate_code is not None
            and type(candidate_code) is not MaterialReceiptFailureCode
        ):
            return None, ReviewFailureCode.INTERNAL_FAILURE, None
        return None, failure_code, candidate_code
    except Exception:
        return None, ReviewFailureCode.INTERNAL_FAILURE, None
    return result, None, None


def _candidate_capability() -> _CreateCandidateCapability:
    return _TerminalCreateCandidateCapability()


def _review_safe_result(result: object) -> ReceiptForReview | None:
    """Return only a validated result; quarantine malformed-object failures."""

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
    except Exception:
        return None
    return result if valid else None


def _map_candidate_request(
    ingestion_result: IngestionResult,
    trusted_receipt_facts: TrustedReceiptFacts,
) -> tuple[
    ReceiptCandidateRequest | None,
    CandidateInputFailureCode | None,
    bool,
]:
    """Quarantine mapper failure graphs while preserving bounded input codes."""

    try:
        request = build_receipt_candidate_request(
            ingestion_result,
            trusted_receipt_facts,
        )
    except CandidateInputError as exc:
        try:
            code = exc.code
        except Exception:
            return None, None, True
        if type(code) is CandidateInputFailureCode:
            return None, code, False
        return None, None, True
    except Exception:
        return None, None, True
    return request, None, False


def _source_context(request: ReceiptCandidateRequest) -> SourceContext | None:
    """Quarantine malformed source failures without preserving their context."""

    try:
        return SourceContext(request.source_asset_reference)
    except Exception:
        return None


def _capture_candidate_creator(
    actor_context: ActorContext | None,
) -> tuple[str | None, ReviewFailureCode | None]:
    if actor_context is None:
        return None, ReviewFailureCode.ACTOR_REQUIRED
    try:
        validated_context = ActorContext.validate(actor_context)
        validated_reference = validated_context.actor_reference
    except (AttributeError, TypeError, ValueError):
        return None, ReviewFailureCode.ACTOR_INVALID
    try:
        return (
            authorize_candidate_creation_actor_reference(validated_reference),
            None,
        )
    except ReviewApplicationError as exc:
        return None, (
            exc.code
            if exc.code is ReviewFailureCode.ACTOR_UNAUTHORIZED
            else ReviewFailureCode.INTERNAL_FAILURE
        )


async def create_review_candidate_from_ingestion(
    ingestion_result: IngestionResult,
    trusted_receipt_facts: TrustedReceiptFacts,
    actor_context: ActorContext | None = None,
) -> ReceiptForReview:
    """Map verified evidence and perform exactly one candidate-create operation."""

    created_by_actor_reference, actor_failure = _capture_candidate_creator(actor_context)
    actor_context = None
    if actor_failure is not None:
        raise ReviewApplicationError(actor_failure) from None
    if created_by_actor_reference is None:
        raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from None
    request, input_failure, internal_mapping_failure = _map_candidate_request(
        ingestion_result,
        trusted_receipt_facts,
    )
    if input_failure is not None:
        raise CandidateInputError(input_failure)
    if internal_mapping_failure or request is None:
        raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE)
    source_context = _source_context(request)
    if source_context is None:
        raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_INVALID)
    result = await _candidate_capability().create_candidate(
        request, source_context, created_by_actor_reference
    )
    safe_result = _review_safe_result(result)
    result = None
    if safe_result is None:
        raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE)
    return safe_result
