"""Internal/manual Stage 0.33C controlled candidate-create callable."""

from __future__ import annotations

from dataclasses import dataclass

from core.material_receipts.models import ReceiptForReview

from .candidate_create_authorization import authorize_and_consume_candidate_create
from .candidate_input import IngestionResult, TrustedReceiptFacts
from .create_from_ingestion import create_review_candidate_from_ingestion
from .review_use_cases import ActorContext


@dataclass(frozen=True, slots=True)
class ControlledCandidateCreateRequest:
    ingestion_result: IngestionResult
    trusted_receipt_facts: TrustedReceiptFacts

    def __post_init__(self) -> None:
        if type(self.ingestion_result) is not IngestionResult:
            raise TypeError("ingestion_result must be IngestionResult")
        if type(self.trusted_receipt_facts) is not TrustedReceiptFacts:
            raise TypeError("trusted_receipt_facts must be TrustedReceiptFacts")
        TrustedReceiptFacts.validate(self.trusted_receipt_facts)


async def controlled_create_review_candidate(
    request: ControlledCandidateCreateRequest,
) -> ReceiptForReview:
    """Consume one authorization, then invoke the existing governed path once."""

    if type(request) is not ControlledCandidateCreateRequest:
        raise TypeError("request must be ControlledCandidateCreateRequest")
    claim = authorize_and_consume_candidate_create(
        request.ingestion_result,
        request.trusted_receipt_facts,
    )
    actor = ActorContext(claim.operator_actor_reference)
    return await create_review_candidate_from_ingestion(
        request.ingestion_result,
        request.trusted_receipt_facts,
        actor,
    )
