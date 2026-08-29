"""Bounded semantic evidence for Stage 0.33C controlled candidate creation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import json
import os
import re
from typing import Protocol


class ClaimOutcome(str, Enum):
    CLAIMED = "CLAIMED"
    CONSUMED = "CONSUMED"
    INVALID = "INVALID"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class DurabilityOutcome(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class ResultClassification(str, Enum):
    CREATED = "CREATED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


_SAFE_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, slots=True)
class CandidateCreateEvidence:
    correlation_id: str
    authorization_id: str
    authorization_artifact_sha256: str
    source_evidence_sha256: str
    operator_reference: str
    claim_outcome: ClaimOutcome
    durability_outcome: DurabilityOutcome
    db_capability_attempted: bool
    candidate_id: str | None
    candidate_status: str | None
    receipt_row_effect: int
    item_row_effect: int
    confirmation_effect: int
    posting_effect: int
    inventory_effect: int
    stock_effect: int
    result_classification: ResultClassification

    def __post_init__(self) -> None:
        for value in (
            self.correlation_id,
            self.authorization_id,
            self.operator_reference,
        ):
            if type(value) is not str or not _SAFE_ID.fullmatch(value):
                raise ValueError("unsafe evidence identifier")
        for value in (
            self.authorization_artifact_sha256,
            self.source_evidence_sha256,
        ):
            if type(value) is not str or not _SHA256.fullmatch(value):
                raise ValueError("invalid evidence digest")
        if type(self.db_capability_attempted) is not bool:
            raise TypeError("db_capability_attempted must be bool")
        if self.candidate_id is not None and (
            type(self.candidate_id) is not str
            or not _SAFE_ID.fullmatch(self.candidate_id)
        ):
            raise ValueError("unsafe candidate identifier")
        if self.candidate_status not in {None, "NEEDS_REVIEW"}:
            raise ValueError("candidate status is not governed")
        effects = (
            self.receipt_row_effect,
            self.item_row_effect,
            self.confirmation_effect,
            self.posting_effect,
            self.inventory_effect,
            self.stock_effect,
        )
        if any(type(value) is not int or value < 0 for value in effects):
            raise ValueError("invalid evidence effect")
        if any(
            value != 0
            for value in (
                self.confirmation_effect,
                self.posting_effect,
                self.inventory_effect,
                self.stock_effect,
            )
        ):
            raise ValueError("non-governed effect")


class DurableEvidenceSink(Protocol):
    def write(self, payload: bytes) -> None: ...

    def flush(self) -> None: ...

    def fileno(self) -> int: ...


def serialize_candidate_create_evidence(evidence: CandidateCreateEvidence) -> bytes:
    value = asdict(evidence)
    value["claim_outcome"] = evidence.claim_outcome.value
    value["durability_outcome"] = evidence.durability_outcome.value
    value["result_classification"] = evidence.result_classification.value
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def write_candidate_create_evidence(
    evidence: CandidateCreateEvidence, sink: DurableEvidenceSink
) -> None:
    """Write one bounded record durably; the caller injects the sink."""

    payload = serialize_candidate_create_evidence(evidence)
    if len(payload) > 4096:
        raise ValueError("evidence record exceeds bound")
    sink.write(payload)
    sink.flush()
    os.fsync(sink.fileno())
