"""Immutable contracts for material-receipt candidate operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from .errors import MaterialReceiptError, MaterialReceiptFailureCode


class ReceiptStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    CONFIRMED = "CONFIRMED"
    POSTED = "POSTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class MaterialUnit(str, Enum):
    SHEET = "sheet"
    PCS = "pcs"
    KG = "kg"
    ROLL = "roll"
    PACK = "pack"


def _text(value: object, field: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-blank text")


def _decimal(value: object, field: str) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{field} must be a finite Decimal")
    return value


@dataclass(frozen=True, slots=True)
class ReceiptItemCandidate:
    receipt_item_id: UUID
    line_number: int
    candidate_material_description: str | None
    canonical_display_name: str | None
    size_description: str | None
    specification: str | None
    material_id: UUID | None
    full_colly_count: int
    qty_per_full_colly: Decimal | None
    partial_qty: Decimal
    total_qty: Decimal
    unit: str

    def __post_init__(self) -> None:
        if type(self.receipt_item_id) is not UUID:
            raise ValueError("receipt_item_id must be a UUID")
        if type(self.line_number) is not int or self.line_number <= 0:
            raise ValueError("line_number must be a positive integer")
        for field in (
            "candidate_material_description",
            "canonical_display_name",
            "size_description",
            "specification",
        ):
            _text(getattr(self, field), field, optional=True)
        if self.material_id is not None and type(self.material_id) is not UUID:
            raise ValueError("material_id must be a UUID or None")
        if type(self.full_colly_count) is not int or self.full_colly_count < 0:
            raise ValueError("full_colly_count must be a nonnegative integer")
        partial = _decimal(self.partial_qty, "partial_qty")
        total = _decimal(self.total_qty, "total_qty")
        if partial < 0 or total <= 0:
            raise ValueError("quantities must be nonnegative and total_qty positive")
        if self.full_colly_count == 0:
            if self.qty_per_full_colly is not None:
                raise ValueError("qty_per_full_colly must be None without full colly")
            per_colly = Decimal(0)
        else:
            if self.qty_per_full_colly is None:
                raise ValueError("qty_per_full_colly is required with full colly")
            per_colly = _decimal(self.qty_per_full_colly, "qty_per_full_colly")
            if per_colly <= 0:
                raise ValueError("qty_per_full_colly must be positive")
        if self.unit not in {unit.value for unit in MaterialUnit}:
            raise ValueError("unit is not in the governed vocabulary")
        if total != Decimal(self.full_colly_count) * per_colly + partial:
            raise MaterialReceiptError(
                MaterialReceiptFailureCode.PACKAGING_FORMULA_INVALID
            )
        if self.unit == MaterialUnit.SHEET.value:
            values = (partial, total) + (() if self.qty_per_full_colly is None else (per_colly,))
            if any(value != value.to_integral_value() for value in values):
                raise ValueError("sheet quantities must be integral")


@dataclass(frozen=True, slots=True)
class ReceiptCandidateRequest:
    receipt_id: UUID
    supplier_name: str
    document_number: str | None
    document_date: date | None
    received_at: datetime
    source_asset_reference: str
    items: tuple[ReceiptItemCandidate, ...]

    def __post_init__(self) -> None:
        if type(self.receipt_id) is not UUID:
            raise ValueError("receipt_id must be a UUID")
        _text(self.supplier_name, "supplier_name")
        _text(self.document_number, "document_number", optional=True)
        if self.document_date is not None and type(self.document_date) is not date:
            raise ValueError("document_date must be a date or None")
        if not isinstance(self.received_at, datetime) or self.received_at.tzinfo is None:
            raise ValueError("received_at must be timezone-aware")
        _text(self.source_asset_reference, "source_asset_reference")
        if type(self.items) is not tuple or not self.items:
            raise ValueError("items must be a non-empty tuple")
        if any(type(item) is not ReceiptItemCandidate for item in self.items):
            raise ValueError("items must contain ReceiptItemCandidate values")
        ids = [item.receipt_item_id for item in self.items]
        lines = [item.line_number for item in self.items]
        if len(ids) != len(set(ids)) or len(lines) != len(set(lines)):
            raise ValueError("receipt item IDs and line numbers must be unique")


@dataclass(frozen=True, slots=True)
class ReceiptItemView:
    receipt_item_id: UUID
    line_number: int
    candidate_material_description: str | None
    canonical_display_name: str | None
    size_description: str | None
    specification: str | None
    material_id: UUID | None
    full_colly_count: int
    qty_per_full_colly: Decimal | None
    partial_qty: Decimal
    total_qty: Decimal
    unit: str
    status: ReceiptStatus


@dataclass(frozen=True, slots=True)
class ReceiptForReview:
    receipt_id: UUID
    supplier_name: str
    document_number: str | None
    document_date: date | None
    received_at: datetime
    source_asset_reference: str
    status: ReceiptStatus
    version: int
    confirmed_version: int | None
    confirmed_at: datetime | None
    confirmation_actor_reference: str | None
    items: tuple[ReceiptItemView, ...]


@dataclass(frozen=True, slots=True)
class ReceiptDecision:
    receipt_id: UUID
    status: ReceiptStatus
    version: int
