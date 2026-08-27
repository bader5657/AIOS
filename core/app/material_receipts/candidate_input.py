"""Inert Stage 0.31A ingestion-evidence to candidate-input mapper."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Decimal
import json
import os
from pathlib import Path
from stat import S_ISREG
from typing import NoReturn
import unicodedata
from uuid import UUID, uuid4

from core.app.input_classifier import InputType
from core.event import EventDeliveryFailureCode
from core.ingestion.universal_ingestion import IngestionResult
from core.material_receipts.models import ReceiptCandidateRequest, ReceiptItemCandidate
from core.storage.document_manifest import validate_manifest

from .candidate_input_errors import CandidateInputError, CandidateInputFailureCode
from .review_use_cases import SourceContext


MAX_RECEIPT_ITEMS = 500
MAX_FULL_COLLY_COUNT = 1_000_000
MAX_QTY_PER_FULL_COLLY = Decimal("1000000")
MAX_PARTIAL_QTY = Decimal("1000000000")
MAX_TOTAL_QTY = Decimal("1000000000")
MAX_DECIMAL_SCALE = 6
MAX_DECIMAL_PRECISION = 20
_UNITS = frozenset({"sheet", "pcs", "kg", "roll", "pack"})


def _fail(code: CandidateInputFailureCode) -> NoReturn:
    raise CandidateInputError(code)


def _canonical_text(
    value: object,
    *,
    optional: bool,
    maximum: int,
) -> None:
    if optional and value is None:
        return
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or any(unicodedata.category(character) in {"Cc", "Cs"} for character in value)
    ):
        _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
    if len(value) > maximum:
        _fail(CandidateInputFailureCode.LIMIT_EXCEEDED)


def _decimal(value: object, *, maximum: Decimal) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        _fail(CandidateInputFailureCode.DECIMAL_POLICY_INVALID)
    sign, digits, exponent = value.as_tuple()
    del sign
    scale = max(-exponent, 0)
    precision = len(digits) + max(exponent, 0)
    if scale > MAX_DECIMAL_SCALE or precision > MAX_DECIMAL_PRECISION:
        _fail(CandidateInputFailureCode.DECIMAL_POLICY_INVALID)
    if value > maximum:
        _fail(CandidateInputFailureCode.LIMIT_EXCEEDED)
    return value


@dataclass(frozen=True, slots=True)
class TrustedReceiptItemFacts:
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
        self._validate_values(
            self.line_number,
            self.candidate_material_description,
            self.canonical_display_name,
            self.size_description,
            self.specification,
            self.material_id,
            self.full_colly_count,
            self.qty_per_full_colly,
            self.partial_qty,
            self.total_qty,
            self.unit,
        )

    @staticmethod
    def _validate_values(
        line_number: object,
        candidate_material_description: object,
        canonical_display_name: object,
        size_description: object,
        specification: object,
        material_id: object,
        full_colly_count: object,
        qty_per_full_colly: object,
        partial_qty: object,
        total_qty: object,
        unit: object,
    ) -> None:
        if type(line_number) is not int or line_number <= 0:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        for value in (
            candidate_material_description,
            canonical_display_name,
            size_description,
            specification,
        ):
            _canonical_text(value, optional=True, maximum=512)
        if material_id is not None and type(material_id) is not UUID:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if (
            type(full_colly_count) is not int
            or full_colly_count < 0
        ):
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if full_colly_count > MAX_FULL_COLLY_COUNT:
            _fail(CandidateInputFailureCode.LIMIT_EXCEEDED)

        partial = _decimal(partial_qty, maximum=MAX_PARTIAL_QTY)
        total = _decimal(total_qty, maximum=MAX_TOTAL_QTY)
        if partial < 0:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if total <= 0:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)

        if full_colly_count == 0:
            if qty_per_full_colly is not None:
                _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
            per_colly = Decimal(0)
        else:
            if qty_per_full_colly is None:
                _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
            per_colly = _decimal(
                qty_per_full_colly,
                maximum=MAX_QTY_PER_FULL_COLLY,
            )
            if per_colly <= 0:
                _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)

        if type(unit) is not str or unit not in _UNITS:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if total != Decimal(full_colly_count) * per_colly + partial:
            _fail(CandidateInputFailureCode.PACKAGING_FORMULA_INVALID)
        if unit == "sheet":
            quantities = (partial, total)
            if qty_per_full_colly is not None:
                quantities += (per_colly,)
            if any(value != value.to_integral_value() for value in quantities):
                _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)

    @classmethod
    def validate(cls, value: object) -> TrustedReceiptItemFacts:
        if type(value) is not cls:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        try:
            values = (
                value.line_number,
                value.candidate_material_description,
                value.canonical_display_name,
                value.size_description,
                value.specification,
                value.material_id,
                value.full_colly_count,
                value.qty_per_full_colly,
                value.partial_qty,
                value.total_qty,
                value.unit,
            )
        except AttributeError:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        cls._validate_values(*values)
        return value


@dataclass(frozen=True, slots=True)
class TrustedReceiptFacts:
    supplier_name: str
    document_number: str | None
    document_date: date | None
    received_at: datetime
    items: tuple[TrustedReceiptItemFacts, ...]

    def __post_init__(self) -> None:
        self._validate_values(
            self.supplier_name,
            self.document_number,
            self.document_date,
            self.received_at,
            self.items,
        )

    @staticmethod
    def _validate_values(
        supplier_name: object,
        document_number: object,
        document_date: object,
        received_at: object,
        items: object,
    ) -> None:
        _canonical_text(supplier_name, optional=False, maximum=128)
        _canonical_text(document_number, optional=True, maximum=128)
        if document_date is not None and type(document_date) is not date:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if type(received_at) is not datetime or received_at.tzinfo is None:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        try:
            offset = received_at.utcoffset()
        except Exception:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if offset is None:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if type(items) is not tuple:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if not items:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        if len(items) > MAX_RECEIPT_ITEMS:
            _fail(CandidateInputFailureCode.LIMIT_EXCEEDED)
        validated = tuple(TrustedReceiptItemFacts.validate(item) for item in items)
        lines = tuple(item.line_number for item in validated)
        if len(lines) != len(set(lines)):
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)

    @classmethod
    def validate(cls, value: object) -> TrustedReceiptFacts:
        if type(value) is not cls:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        try:
            values = (
                value.supplier_name,
                value.document_number,
                value.document_date,
                value.received_at,
                value.items,
            )
        except AttributeError:
            _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
        cls._validate_values(*values)
        return value


def source_context_from_ingestion_result(result: object) -> SourceContext:
    """Validate the current ingestion evidence values without copying payload data."""

    if type(result) is not IngestionResult:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    try:
        current = {
            field.name: getattr(result, field.name)
            for field in fields(IngestionResult)
        }
    except AttributeError:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    manifest_path = current["manifest_path"]
    register_handoff_ready = current["register_handoff_ready"]
    process_handoff_ready = current["process_handoff_ready"]
    route_handoff_ready = current["route_handoff_ready"]
    respond_acknowledgement_ready = current["respond_acknowledgement_ready"]
    registration_succeeded = current["registration_succeeded"]
    registry_record_id = current["registry_record_id"]
    event_publication_attempted = current["event_publication_attempted"]
    event_delivery_succeeded = current["event_delivery_succeeded"]
    event_delivery_failure_code = current["event_delivery_failure_code"]
    brain_result = current["brain_result"]
    if (
        type(current["input_type"]) is not InputType
        or type(current["recognized_input_type"]) is not InputType
        or (current["stored_path"] is not None and type(current["stored_path"]) is not str)
        or type(manifest_path) is not str
        or type(current["metadata"]) is not dict
        or type(current["text"]) is not str
    ):
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    boolean_fields = (
        "register_handoff_ready",
        "process_handoff_ready",
        "route_handoff_ready",
        "respond_acknowledgement_ready",
        "registration_succeeded",
        "event_publication_attempted",
        "event_delivery_succeeded",
    )
    if any(type(current[name]) is not bool for name in boolean_fields):
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if register_handoff_ready is not True:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if process_handoff_ready is not False or respond_acknowledgement_ready is not True:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if registration_succeeded:
        if type(registry_record_id) is not int or registry_record_id <= 0:
            _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    elif registry_record_id is not None:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if event_publication_attempted:
        if not registration_succeeded:
            _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
        if event_delivery_succeeded:
            if event_delivery_failure_code is not None:
                _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
        elif type(event_delivery_failure_code) is not EventDeliveryFailureCode:
            _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    elif event_delivery_succeeded or event_delivery_failure_code is not None:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if route_handoff_ready and not event_delivery_succeeded:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if brain_result is not None:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    try:
        context = SourceContext(manifest_path, registry_record_id)
    except (TypeError, ValueError):
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    _verified_manifest_id(context)
    return context



def _verified_manifest_id(source_context: SourceContext) -> UUID:
    """Read exactly one canonical manifest without following symlinks."""

    SourceContext.validate(source_context)
    path = source_context.manifest_reference
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        status = os.lstat(path)
        if not S_ISREG(status.st_mode):
            _fail(CandidateInputFailureCode.RETAINED_MANIFEST_INVALID)
        descriptor = os.open(path, flags)
        if not S_ISREG(os.fstat(descriptor).st_mode):
            _fail(CandidateInputFailureCode.RETAINED_MANIFEST_INVALID)
        with os.fdopen(descriptor, "r", encoding="utf-8") as manifest_file:
            descriptor = None
            manifest = json.load(manifest_file)
        validate_manifest(manifest)
        filename_id = UUID(Path(path).stem)
        if manifest.get("manifest_id") != str(filename_id):
            _fail(CandidateInputFailureCode.RETAINED_MANIFEST_INVALID)
        return filename_id
    except CandidateInputError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        _fail(CandidateInputFailureCode.RETAINED_MANIFEST_INVALID)
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _next_uuid(id_factory: Callable[[], UUID], used: set[UUID]) -> UUID:
    try:
        generated = id_factory()
    except Exception:
        _fail(CandidateInputFailureCode.ID_GENERATION_INVALID)
    if type(generated) is not UUID or generated.version != 4 or generated in used:
        _fail(CandidateInputFailureCode.ID_GENERATION_INVALID)
    used.add(generated)
    return generated


def build_receipt_candidate_request(
    ingestion_evidence: object,
    trusted_receipt_facts: object,
    *,
    id_factory: Callable[[], UUID] = uuid4,
) -> ReceiptCandidateRequest:
    """Build an immutable request without persistence or operational authority."""

    if type(ingestion_evidence) is not IngestionResult:
        _fail(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)
    if type(trusted_receipt_facts) is not TrustedReceiptFacts:
        _fail(CandidateInputFailureCode.TRUSTED_FACTS_INVALID)
    facts = TrustedReceiptFacts.validate(trusted_receipt_facts)
    source_context = source_context_from_ingestion_result(ingestion_evidence)
    if not callable(id_factory):
        _fail(CandidateInputFailureCode.ID_GENERATION_INVALID)

    used: set[UUID] = set()
    receipt_id = _next_uuid(id_factory, used)
    items = tuple(
        ReceiptItemCandidate(
            receipt_item_id=_next_uuid(id_factory, used),
            line_number=item.line_number,
            candidate_material_description=item.candidate_material_description,
            canonical_display_name=item.canonical_display_name,
            size_description=item.size_description,
            specification=item.specification,
            material_id=item.material_id,
            full_colly_count=item.full_colly_count,
            qty_per_full_colly=item.qty_per_full_colly,
            partial_qty=item.partial_qty,
            total_qty=item.total_qty,
            unit=item.unit,
        )
        for item in facts.items
    )
    return ReceiptCandidateRequest(
        receipt_id=receipt_id,
        supplier_name=facts.supplier_name,
        document_number=facts.document_number,
        document_date=facts.document_date,
        received_at=facts.received_at,
        source_asset_reference=source_context.manifest_reference,
        items=items,
    )
