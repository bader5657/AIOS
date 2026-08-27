from __future__ import annotations

import functools
import importlib
import inspect
import os
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from types import FunctionType, MethodType
from uuid import uuid4

import psycopg
import pytest

from core.app.input_classifier import InputType
from core.app.material_receipts import create_from_ingestion
from core.app.material_receipts.candidate_input import (
    TrustedReceiptFacts,
    TrustedReceiptItemFacts,
)
from core.app.material_receipts.candidate_input_errors import (
    CandidateInputError,
    CandidateInputFailureCode,
)
from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode
from core.app.material_receipts.review_use_cases import ReviewFacade, SourceContext
from core.ingestion.universal_ingestion import IngestionResult
from core.inventory_posting.repository import (
    InventoryPostingRepository,
    PostingDatabaseConfig,
)
from core.material_receipts.models import (
    ReceiptCandidateRequest,
    ReceiptForReview,
    ReceiptItemCandidate,
    ReceiptItemView,
    ReceiptStatus,
)
from core.material_receipts.repository import (
    CandidateDatabaseConfig,
    MaterialReceiptRepository,
)


def request(*, source: str | None = None) -> ReceiptCandidateRequest:
    receipt_id = uuid4()
    item_id = uuid4()
    return ReceiptCandidateRequest(
        receipt_id=receipt_id,
        supplier_name="PT Example",
        document_number="DO-31B",
        document_date=date(2026, 8, 27),
        received_at=datetime(2026, 8, 27, tzinfo=timezone.utc),
        source_asset_reference=source
        or f"/opt/aios/data/documents/manifests/{uuid4()}.json",
        items=(
            ReceiptItemCandidate(
                receipt_item_id=item_id,
                line_number=1,
                candidate_material_description="Steel sheet",
                canonical_display_name=None,
                size_description=None,
                specification=None,
                material_id=None,
                full_colly_count=2,
                qty_per_full_colly=Decimal("50"),
                partial_qty=Decimal("3"),
                total_qty=Decimal("103"),
                unit="sheet",
            ),
        ),
    )


def review_result(candidate: ReceiptCandidateRequest) -> ReceiptForReview:
    item = candidate.items[0]
    return ReceiptForReview(
        candidate.receipt_id,
        candidate.supplier_name,
        candidate.document_number,
        candidate.document_date,
        candidate.received_at,
        candidate.source_asset_reference,
        ReceiptStatus.NEEDS_REVIEW,
        1,
        None,
        None,
        None,
        (
            ReceiptItemView(
                item.receipt_item_id,
                item.line_number,
                item.candidate_material_description,
                item.canonical_display_name,
                item.size_description,
                item.specification,
                item.material_id,
                item.full_colly_count,
                item.qty_per_full_colly,
                item.partial_qty,
                item.total_qty,
                item.unit,
                ReceiptStatus.NEEDS_REVIEW,
            ),
        ),
    )


class RecordingCreateCapability:
    __slots__ = ("calls", "result")

    def __init__(self, result: ReceiptForReview) -> None:
        self.calls: list[tuple[ReceiptCandidateRequest, SourceContext]] = []
        self.result = result

    async def create_candidate(self, candidate, source_context):
        self.calls.append((candidate, source_context))
        return self.result


def trusted_facts() -> TrustedReceiptFacts:
    return TrustedReceiptFacts(
        supplier_name="PT Example",
        document_number="DO-31B",
        document_date=date(2026, 8, 27),
        received_at=datetime(2026, 8, 27, tzinfo=timezone.utc),
        items=(
            TrustedReceiptItemFacts(
                line_number=1,
                candidate_material_description="Steel sheet",
                canonical_display_name=None,
                size_description=None,
                specification=None,
                material_id=None,
                full_colly_count=2,
                qty_per_full_colly=Decimal("50"),
                partial_qty=Decimal("3"),
                total_qty=Decimal("103"),
                unit="sheet",
            ),
        ),
    )

def ingestion_evidence() -> IngestionResult:
    return IngestionResult(
        input_type=InputType.TEXT,
        recognized_input_type=InputType.TEXT,
        stored_path=None,
        manifest_path=f"/opt/aios/data/documents/manifests/{uuid4()}.json",
        metadata={},
        text="untrusted",
        register_handoff_ready=True,
        process_handoff_ready=False,
        route_handoff_ready=False,
        respond_acknowledgement_ready=True,
    )



@pytest.mark.asyncio
async def test_public_api_maps_once_then_creates_once(monkeypatch) -> None:
    candidate = request()
    result = review_result(candidate)
    capability = RecordingCreateCapability(result)
    mapper_calls: list[tuple[object, object]] = []
    evidence = object()
    facts = object()

    def mapper(received_evidence, received_facts):
        mapper_calls.append((received_evidence, received_facts))
        return candidate

    monkeypatch.setattr(create_from_ingestion, "build_receipt_candidate_request", mapper)
    monkeypatch.setattr(create_from_ingestion, "_candidate_capability", lambda: capability)

    actual = await create_from_ingestion.create_review_candidate_from_ingestion(
        evidence, facts
    )

    assert actual is result
    assert mapper_calls == [(evidence, facts)]
    assert capability.calls == [
        (candidate, SourceContext(candidate.source_asset_reference))
    ]


def test_public_surface_has_one_two_input_operation() -> None:
    assert create_from_ingestion.__all__ == (
        "create_review_candidate_from_ingestion",
    )
    signature = inspect.signature(
        create_from_ingestion.create_review_candidate_from_ingestion
    )
    assert tuple(signature.parameters) == (
        "ingestion_result",
        "trusted_receipt_facts",
    )
    assert not hasattr(create_from_ingestion, "ActorContext")


@pytest.mark.asyncio
async def test_mapper_failure_prevents_capability_construction(monkeypatch) -> None:
    capability_calls = 0

    def fail_mapper(*args):
        raise CandidateInputError(CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE)

    def capability():
        nonlocal capability_calls
        capability_calls += 1
        raise AssertionError("candidate capability must not be constructed")

    monkeypatch.setattr(
        create_from_ingestion, "build_receipt_candidate_request", fail_mapper
    )
    monkeypatch.setattr(create_from_ingestion, "_candidate_capability", capability)

    with pytest.raises(CandidateInputError) as caught:
        await create_from_ingestion.create_review_candidate_from_ingestion(
            object(), object()
        )
    assert caught.value.code is CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE
    assert capability_calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("evidence", "facts", "code"),
    [
        (object(), trusted_facts(), CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE),
        (ingestion_evidence(), object(), CandidateInputFailureCode.TRUSTED_FACTS_INVALID),
    ],
)
async def test_invalid_inputs_never_construct_candidate_capability(
    monkeypatch, evidence, facts, code
) -> None:
    calls = 0

    def forbidden():
        nonlocal calls
        calls += 1
        raise AssertionError("candidate capability must remain unreachable")

    monkeypatch.setattr(create_from_ingestion, "_candidate_capability", forbidden)
    with pytest.raises(CandidateInputError) as caught:
        await create_from_ingestion.create_review_candidate_from_ingestion(
            evidence, facts
        )
    assert caught.value.code is code
    assert calls == 0


@pytest.mark.asyncio
async def test_forged_trusted_facts_prevents_candidate_capability(monkeypatch) -> None:
    forged = object.__new__(TrustedReceiptFacts)
    for field in fields(TrustedReceiptFacts):
        object.__setattr__(forged, field.name, getattr(trusted_facts(), field.name))
    object.__setattr__(forged, "supplier_name", " forged")
    calls = 0

    def forbidden():
        nonlocal calls
        calls += 1
        raise AssertionError("candidate capability must remain unreachable")

    monkeypatch.setattr(create_from_ingestion, "_candidate_capability", forbidden)
    with pytest.raises(CandidateInputError) as caught:
        await create_from_ingestion.create_review_candidate_from_ingestion(
            ingestion_evidence(), forged
        )
    assert caught.value.code is CandidateInputFailureCode.TRUSTED_FACTS_INVALID
    assert calls == 0


@pytest.mark.asyncio
async def test_non_authoritative_mapper_source_is_rejected_before_create(monkeypatch) -> None:
    candidate = request(source="asset:caller-override")
    calls = 0
    monkeypatch.setattr(
        create_from_ingestion,
        "build_receipt_candidate_request",
        lambda *args: candidate,
    )

    def forbidden():
        nonlocal calls
        calls += 1
        raise AssertionError("candidate capability must remain unreachable")

    monkeypatch.setattr(create_from_ingestion, "_candidate_capability", forbidden)
    with pytest.raises(ReviewApplicationError) as caught:
        await create_from_ingestion.create_review_candidate_from_ingestion(
            object(), object()
        )
    assert caught.value.code is ReviewFailureCode.SOURCE_IDENTITY_INVALID
    assert calls == 0


@pytest.mark.asyncio
async def test_non_review_safe_result_fails_closed(monkeypatch) -> None:
    candidate = request()
    unsafe = review_result(candidate)
    object.__setattr__(unsafe, "status", ReceiptStatus.CONFIRMED)
    capability = RecordingCreateCapability(unsafe)
    monkeypatch.setattr(
        create_from_ingestion,
        "build_receipt_candidate_request",
        lambda *args: candidate,
    )
    monkeypatch.setattr(create_from_ingestion, "_candidate_capability", lambda: capability)
    with pytest.raises(ReviewApplicationError) as caught:
        await create_from_ingestion.create_review_candidate_from_ingestion(
            object(), object()
        )
    assert caught.value.code is ReviewFailureCode.INTERNAL_FAILURE
    assert len(capability.calls) == 1


def reachable_objects(root: object) -> tuple[object, ...]:
    pending = [root]
    seen: dict[int, object] = {}
    atomic = (str, bytes, int, float, bool, type(None), type)
    while pending:
        value = pending.pop()
        if id(value) in seen:
            continue
        seen[id(value)] = value
        if isinstance(value, atomic):
            continue
        if is_dataclass(value) and not isinstance(value, type):
            pending.extend(getattr(value, field.name) for field in fields(value))
        mapping = getattr(value, "__dict__", None)
        if isinstance(mapping, dict):
            pending.extend(mapping.values())
        slots = getattr(type(value), "__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        for slot in slots:
            name = slot
            if slot.startswith("__") and not slot.endswith("__"):
                name = f"_{type(value).__name__}{slot}"
            if hasattr(value, name):
                pending.append(getattr(value, name))
        if isinstance(value, MethodType):
            pending.append(value.__self__)
        if isinstance(value, FunctionType) and value.__closure__:
            pending.extend(cell.cell_contents for cell in value.__closure__)
        pending.extend(
            descriptor
            for name, descriptor in vars(type(value)).items()
            if not name.startswith("__")
        )
        if isinstance(value, functools.partial):
            pending.extend((value.func, *value.args, *value.keywords.values()))
    return tuple(seen.values())


def test_terminal_create_capability_object_graph_is_empty_and_create_only() -> None:
    capability = create_from_ingestion._TerminalCreateCandidateCapability()
    reachable = reachable_objects(capability)
    forbidden_types = (
        ReviewFacade,
        MaterialReceiptRepository,
        CandidateDatabaseConfig,
        InventoryPostingRepository,
        PostingDatabaseConfig,
    )
    assert not any(
        isinstance(value, str)
        and (
            "postgresql://" in value
            or "password=" in value
            or "AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD" in value
        )
        for value in reachable
    )
    assert not any(isinstance(value, forbidden_types) for value in reachable)
    assert not hasattr(capability, "__dict__")
    public = {
        name
        for name in dir(capability)
        if not name.startswith("_")
    }
    assert public == {"create_candidate"}
    forbidden_names = {
        "confirm_receipt",
        "post_confirmed_receipt",
        "revise_candidate",
        "reject_receipt",
        "cancel_receipt",
        "cancel_receipt_item",
        "execute",
        "dispatch",
        "repository",
        "connection",
        "transaction",
    }
    assert all(not hasattr(capability, name) for name in forbidden_names)


def test_import_and_inert_construction_have_zero_side_effects(monkeypatch) -> None:
    connection_calls = 0
    environment_reads: list[str] = []
    before = dict(os.environ)

    async def forbidden_connection(*args, **kwargs):
        nonlocal connection_calls
        connection_calls += 1
        raise AssertionError("import or construction must not connect")

    def record_get(name, default=None):
        environment_reads.append(name)
        return default

    monkeypatch.setattr(psycopg.AsyncConnection, "connect", forbidden_connection)
    monkeypatch.setattr(os.environ, "get", record_get)
    importlib.reload(create_from_ingestion)
    capability = create_from_ingestion._TerminalCreateCandidateCapability()

    assert type(capability).__slots__ == ()
    assert connection_calls == 0
    assert environment_reads == []
    assert dict(os.environ) == before
