"""Outermost composition root for review-only receipt orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from stat import S_ISREG
from uuid import UUID

from core.material_receipts.models import ReceiptCandidateRequest, ReceiptForReview

from .ports import RetainedManifestIdentity
from .results import ReviewApplicationError, ReviewFailureCode
from .review_use_cases import ReviewFacade, SourceContext


class _FilesystemRetainedEvidenceVerifier:
    """Verify only canonical manifest identities in the retained evidence root."""

    __slots__ = ()

    def is_retained(self, source_context: RetainedManifestIdentity) -> bool:
        try:
            status = os.stat(source_context.manifest_reference, follow_symlinks=False)
        except OSError:
            return False
        return S_ISREG(status.st_mode)


class _CandidateReviewOperations:
    """Stateless, source-safe candidate operations with no retained repository."""

    __slots__ = ()

    @staticmethod
    def _require_retained(reference: str) -> None:
        try:
            context = SourceContext(reference)
        except (TypeError, ValueError) as exc:
            raise ReviewApplicationError(
                ReviewFailureCode.SOURCE_IDENTITY_INVALID
            ) from exc
        if not _FilesystemRetainedEvidenceVerifier().is_retained(context):
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_INVALID)

    async def create_candidate(
        self, request: ReceiptCandidateRequest, created_by_actor_reference: str
    ) -> ReceiptForReview:
        self._require_retained(request.source_asset_reference)
        from core.material_receipts.repository import MaterialReceiptRepository

        repository = MaterialReceiptRepository.from_environment()
        result = await repository._create_receipt_candidate(
            request, created_by_actor_reference
        )
        self._require_retained(result.source_asset_reference)
        if result.source_asset_reference != request.source_asset_reference:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_CONFLICT)
        return result

    async def revise_candidate(
        self, request: ReceiptCandidateRequest, expected_version: int
    ) -> ReceiptForReview:
        self._require_retained(request.source_asset_reference)
        from core.material_receipts.repository import MaterialReceiptRepository

        repository = MaterialReceiptRepository.from_environment()
        current = await repository.get_receipt_for_review(request.receipt_id)
        self._require_retained(current.source_asset_reference)
        if request.source_asset_reference != current.source_asset_reference:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_CONFLICT)
        result = await repository.revise_receipt_candidate(request, expected_version)
        self._require_retained(result.source_asset_reference)
        if result.source_asset_reference != current.source_asset_reference:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_CONFLICT)
        return result

    async def get_candidate_for_review(
        self, receipt_id: UUID
    ) -> ReceiptForReview:
        from core.material_receipts.repository import MaterialReceiptRepository

        repository = MaterialReceiptRepository.from_environment()
        result = await repository.get_receipt_for_review(receipt_id)
        self._require_retained(result.source_asset_reference)
        return result


@dataclass(frozen=True, slots=True)
class ReviewComposition:
    facade: ReviewFacade


def compose_review_application() -> ReviewComposition:
    """Construct a stateless, inert, review-only capability graph."""

    return ReviewComposition(
        facade=ReviewFacade(
            _CandidateReviewOperations(),
            _FilesystemRetainedEvidenceVerifier(),
        )
    )
