"""Outermost composition root for review-only receipt orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.material_receipts.models import ReceiptCandidateRequest, ReceiptForReview
from core.material_receipts.repository import (
    CandidateDatabaseConfig,
    MaterialReceiptRepository,
)

from .review_use_cases import ReviewFacade


class _RepositoryCandidateReviewAdapter:
    """Hide the broader repository behind the three governed operations."""

    __slots__ = ("__repository",)

    def __init__(self, repository: MaterialReceiptRepository) -> None:
        self.__repository = repository

    async def create_candidate(
        self, request: ReceiptCandidateRequest
    ) -> ReceiptForReview:
        return await self.__repository.create_receipt_candidate(request)

    async def revise_candidate(
        self, request: ReceiptCandidateRequest, expected_version: int
    ) -> ReceiptForReview:
        return await self.__repository.revise_receipt_candidate(
            request, expected_version
        )

    async def get_candidate_for_review(
        self, receipt_id: UUID
    ) -> ReceiptForReview:
        return await self.__repository.get_receipt_for_review(receipt_id)


@dataclass(frozen=True, slots=True)
class ReviewComposition:
    facade: ReviewFacade


def compose_review_application(config: CandidateDatabaseConfig) -> ReviewComposition:
    """Construct an inert review graph; database I/O begins only on use-case calls."""

    if type(config) is not CandidateDatabaseConfig:
        raise TypeError("config must be CandidateDatabaseConfig")
    repository = MaterialReceiptRepository(config)
    candidate_port = _RepositoryCandidateReviewAdapter(repository)
    return ReviewComposition(facade=ReviewFacade(candidate_port))


def compose_review_application_from_environment() -> ReviewComposition:
    """Load only the governed candidate credential at the outermost root."""

    repository = MaterialReceiptRepository.from_environment()
    candidate_port = _RepositoryCandidateReviewAdapter(repository)
    return ReviewComposition(facade=ReviewFacade(candidate_port))
