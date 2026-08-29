from __future__ import annotations

from dataclasses import fields
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.app.input_classifier import InputType
from core.app.material_receipts import controlled_candidate_create as controlled
from core.app.material_receipts.candidate_input import (
    TrustedReceiptFacts,
    TrustedReceiptItemFacts,
)
from core.ingestion.universal_ingestion import IngestionResult
from core.material_receipts.models import ReceiptForReview, ReceiptItemView, ReceiptStatus


ACTOR = "operator:550e8400-e29b-41d4-a716-446655440000"


def request() -> controlled.ControlledCandidateCreateRequest:
    evidence = IngestionResult(
        InputType.TEXT, InputType.TEXT, None, "/retained/manifest.json", {}, "x",
        True, False, False, True,
    )
    facts = TrustedReceiptFacts(
        "PT Example", "DO-1", date(2026, 8, 29),
        datetime(2026, 8, 29, tzinfo=timezone.utc),
        (TrustedReceiptItemFacts(1, "Steel", None, None, None, None, 1,
         Decimal("50"), Decimal("0"), Decimal("50"), "sheet"),),
    )
    return controlled.ControlledCandidateCreateRequest(evidence, facts)


def result(current) -> ReceiptForReview:
    item_id = uuid4()
    return ReceiptForReview(
        uuid4(), current.trusted_receipt_facts.supplier_name, "DO-1",
        date(2026, 8, 29), datetime(2026, 8, 29, tzinfo=timezone.utc),
        current.ingestion_result.manifest_path, ReceiptStatus.NEEDS_REVIEW, 1,
        None, None, None,
        (ReceiptItemView(item_id, 1, "Steel", None, None, None, None, 1,
         Decimal("50"), Decimal("0"), Decimal("50"), "sheet",
         ReceiptStatus.NEEDS_REVIEW),),
    )


def test_request_is_exact_frozen_two_field_dto() -> None:
    assert tuple(field.name for field in fields(controlled.ControlledCandidateCreateRequest)) == (
        "ingestion_result", "trusted_receipt_facts"
    )
    with pytest.raises(TypeError):
        controlled.ControlledCandidateCreateRequest(object(), object())


@pytest.mark.asyncio
async def test_authorization_and_durability_precede_exact_one_governed_call(monkeypatch) -> None:
    current = request()
    expected = result(current)
    order: list[object] = []

    def authorize(evidence, facts):
        order.append(("authorized", evidence, facts))
        return SimpleNamespace(operator_actor_reference=ACTOR)

    async def create(evidence, facts, actor):
        order.append(("created", evidence, facts, actor.actor_reference))
        return expected

    monkeypatch.setattr(controlled, "authorize_and_consume_candidate_create", authorize)
    monkeypatch.setattr(controlled, "create_review_candidate_from_ingestion", create)
    actual = await controlled.controlled_create_review_candidate(current)
    assert actual is expected
    assert [entry[0] for entry in order] == ["authorized", "created"]
    assert order[1][3] == ACTOR


@pytest.mark.asyncio
async def test_every_preclaim_failure_has_zero_governed_create_capability(monkeypatch) -> None:
    current = request()
    calls = 0

    def reject(*args):
        raise RuntimeError("disabled, invalid, expired, actor, input, or consumed")

    async def forbidden(*args):
        nonlocal calls
        calls += 1
        raise AssertionError("governed create reached")

    monkeypatch.setattr(controlled, "authorize_and_consume_candidate_create", reject)
    monkeypatch.setattr(controlled, "create_review_candidate_from_ingestion", forbidden)
    with pytest.raises(RuntimeError):
        await controlled.controlled_create_review_candidate(current)
    assert calls == 0


@pytest.mark.asyncio
async def test_no_retry_or_confirmation_posting_inventory_stock_surface(monkeypatch) -> None:
    current = request()
    expected = result(current)
    authorize_calls = 0
    create_calls = 0

    def authorize(*args):
        nonlocal authorize_calls
        authorize_calls += 1
        return SimpleNamespace(operator_actor_reference=ACTOR)

    async def create(*args):
        nonlocal create_calls
        create_calls += 1
        return expected

    monkeypatch.setattr(controlled, "authorize_and_consume_candidate_create", authorize)
    monkeypatch.setattr(controlled, "create_review_candidate_from_ingestion", create)
    actual = await controlled.controlled_create_review_candidate(current)
    assert actual.status is ReceiptStatus.NEEDS_REVIEW
    assert actual.confirmed_at is None
    assert actual.confirmation_actor_reference is None
    assert authorize_calls == create_calls == 1
    source = Path(controlled.__file__).read_text(encoding="utf-8")
    for prohibited in ("confirm_receipt", "post_confirmed_receipt", "inventory_movements", "material_stock"):
        assert prohibited not in source
