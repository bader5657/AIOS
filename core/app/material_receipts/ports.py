"""Narrow candidate-only port for review application orchestration."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from core.material_receipts.models import ReceiptCandidateRequest, ReceiptForReview


class CandidateReviewPort(Protocol):
    """The only persistence operations visible to review use cases."""

    async def create_candidate(
        self, request: ReceiptCandidateRequest
    ) -> ReceiptForReview: ...

    async def revise_candidate(
        self, request: ReceiptCandidateRequest, expected_version: int
    ) -> ReceiptForReview: ...

    async def get_candidate_for_review(
        self, receipt_id: UUID
    ) -> ReceiptForReview: ...
