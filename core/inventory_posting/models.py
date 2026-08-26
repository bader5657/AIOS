"""Immutable request and audit result contracts for inventory posting."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class PostingOutcome(str, Enum):
    POSTED = "POSTED"
    ALREADY_POSTED = "ALREADY_POSTED"


class IdempotencyOutcome(str, Enum):
    CREATED = "CREATED"
    REPLAYED = "REPLAYED"


@dataclass(frozen=True, slots=True)
class PostConfirmedReceiptRequest:
    receipt_id: UUID
    expected_version: int
    actor_reference: str

    def __post_init__(self) -> None:
        if type(self.receipt_id) is not UUID:
            raise ValueError("receipt_id must be a UUID")
        if type(self.expected_version) is not int or self.expected_version <= 0:
            raise ValueError("expected_version must be a positive integer")
        if not isinstance(self.actor_reference, str) or not self.actor_reference.strip():
            raise ValueError("actor_reference must be non-blank text")


@dataclass(frozen=True, slots=True)
class MovementEvidence:
    movement_id: UUID
    source_receipt_item_id: UUID
    material_id: UUID
    quantity_delta: Decimal
    unit: str
    balance_before: Decimal
    balance_after: Decimal


@dataclass(frozen=True, slots=True)
class PostingResult:
    receipt_id: UUID
    version: int
    actor_reference: str
    outcome: PostingOutcome
    idempotency_outcome: IdempotencyOutcome
    posted_at: datetime
    movements: tuple[MovementEvidence, ...]
