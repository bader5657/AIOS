from __future__ import annotations

import io
import json
import os

import pytest

from core.app.material_receipts.candidate_create_evidence import (
    CandidateCreateEvidence,
    ClaimOutcome,
    DurabilityOutcome,
    ResultClassification,
    serialize_candidate_create_evidence,
    write_candidate_create_evidence,
)


def evidence(**overrides) -> CandidateCreateEvidence:
    values = dict(
        correlation_id="stage033c-session",
        authorization_id="550e8400-e29b-41d4-a716-446655440000",
        authorization_artifact_sha256="a" * 64,
        source_evidence_sha256="b" * 64,
        operator_reference="operator:550e8400-e29b-41d4-a716-446655440000",
        claim_outcome=ClaimOutcome.CLAIMED,
        durability_outcome=DurabilityOutcome.COMPLETE,
        db_capability_attempted=True,
        candidate_id="6ba7b810-9dad-4d80-a000-000000000002",
        candidate_status="NEEDS_REVIEW",
        receipt_row_effect=1,
        item_row_effect=2,
        confirmation_effect=0,
        posting_effect=0,
        inventory_effect=0,
        stock_effect=0,
        result_classification=ResultClassification.CREATED,
    )
    values.update(overrides)
    return CandidateCreateEvidence(**values)


def test_schema_is_bounded_deterministic_and_semantic_only() -> None:
    payload = serialize_candidate_create_evidence(evidence())
    assert payload == serialize_candidate_create_evidence(evidence())
    value = json.loads(payload)
    assert len(value) == 17
    assert value["claim_outcome"] == "CLAIMED"
    assert value["durability_outcome"] == "COMPLETE"
    assert value["db_capability_attempted"] is True
    assert value["candidate_status"] == "NEEDS_REVIEW"
    for prohibited in (b"password", b"database_url", b"runtime.env", b"token", b"private_key", b"supplier", b"document"):
        assert prohibited not in payload.lower()


@pytest.mark.parametrize(
    "overrides",
    [
        {"candidate_status": "CONFIRMED"},
        {"confirmation_effect": 1},
        {"posting_effect": 1},
        {"inventory_effect": 1},
        {"stock_effect": 1},
        {"operator_reference": "operator:unsafe payload"},
        {"authorization_artifact_sha256": "not-a-digest"},
    ],
)
def test_unsafe_or_escalated_evidence_is_rejected(overrides) -> None:
    with pytest.raises(ValueError):
        evidence(**overrides)


def test_sink_write_flush_fsync_order(monkeypatch) -> None:
    order: list[str] = []

    class Sink(io.BytesIO):
        def write(self, payload):
            order.append("write")
            return super().write(payload)

        def flush(self):
            order.append("flush")

        def fileno(self):
            order.append("fileno")
            return 99

    monkeypatch.setattr(os, "fsync", lambda fd: order.append(f"fsync:{fd}"))
    write_candidate_create_evidence(evidence(), Sink())
    assert order == ["write", "flush", "fileno", "fsync:99"]
