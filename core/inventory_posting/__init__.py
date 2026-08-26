"""Authoritative inventory posting application boundary."""

from .errors import InventoryPostingError, InventoryPostingFailureCode
from .models import (
    IdempotencyOutcome,
    MovementEvidence,
    PostConfirmedReceiptRequest,
    PostingOutcome,
    PostingResult,
)
from .repository import InventoryPostingRepository
from .service import InventoryPostingService

__all__ = [
    "IdempotencyOutcome",
    "InventoryPostingError",
    "InventoryPostingFailureCode",
    "InventoryPostingRepository",
    "InventoryPostingService",
    "MovementEvidence",
    "PostConfirmedReceiptRequest",
    "PostingOutcome",
    "PostingResult",
]
