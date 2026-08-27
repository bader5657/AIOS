"""Bounded, transport-independent failures for review orchestration."""

from __future__ import annotations

from enum import Enum

from core.material_receipts.errors import MaterialReceiptFailureCode


class ReviewFailureCode(str, Enum):
    SOURCE_IDENTITY_INVALID = "SOURCE_IDENTITY_INVALID"
    SOURCE_IDENTITY_CONFLICT = "SOURCE_IDENTITY_CONFLICT"
    INVALID_REVIEW_REQUEST = "INVALID_REVIEW_REQUEST"
    CANDIDATE_OPERATION_FAILED = "CANDIDATE_OPERATION_FAILED"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"
    SOURCE_ACTIVE_RECEIPT_EXISTS = "SOURCE_ACTIVE_RECEIPT_EXISTS"


class ReviewApplicationError(RuntimeError):
    """Sanitized application failure without infrastructure detail."""

    def __init__(
        self,
        code: ReviewFailureCode,
        *,
        candidate_code: MaterialReceiptFailureCode | None = None,
    ) -> None:
        self.code = code
        self.candidate_code = candidate_code
        super().__init__(code.value)
