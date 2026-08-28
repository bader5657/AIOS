"""Narrow ports for review-only receipt orchestration."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from core.material_receipts.models import ReceiptCandidateRequest, ReceiptForReview

class CandidateReviewPort(Protocol):
    """The only candidate operations visible to review use cases."""

    async def create_candidate(
        self, request: ReceiptCandidateRequest, created_by_actor_reference: str
    ) -> ReceiptForReview: ...

    async def revise_candidate(
        self, request: ReceiptCandidateRequest, expected_version: int
    ) -> ReceiptForReview: ...

    async def get_candidate_for_review(
        self, receipt_id: UUID
    ) -> ReceiptForReview: ...

class RetainedManifestIdentity(Protocol):
    """Read-only canonical manifest identity required by evidence verification."""

    @property
    def manifest_reference(self) -> str: ...

class RetainedEvidenceVerifier(Protocol):
    """Answer only whether one canonical source identity is retained."""

    def is_retained(self, source_context: RetainedManifestIdentity) -> bool: ...
