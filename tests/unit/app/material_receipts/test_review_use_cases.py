from __future__ import annotations

import asyncio
import inspect
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from decimal import Decimal
import uuid

import psycopg
import pytest

from core.app.material_receipts.ports import CandidateReviewPort
from core.app.material_receipts.review_use_cases import (
    ActorContext,
    ReviewFacade,
    SourceContext,
)
from core.app.material_receipts.results import (
    ReviewApplicationError,
    ReviewFailureCode,
)
from core.material_receipts import (
    MaterialReceiptError,
    MaterialReceiptFailureCode,
    ReceiptCandidateRequest,
    ReceiptForReview,
    ReceiptItemCandidate,
    ReceiptItemView,
    ReceiptStatus,
)


def manifest_reference() -> str:
    return f"/opt/aios/data/documents/manifests/{uuid.uuid4()}.json"


def candidate_request(source: str | None = None) -> ReceiptCandidateRequest:
    item = ReceiptItemCandidate(
        receipt_item_id=uuid.uuid4(),
        line_number=1,
        candidate_material_description="EF sheet",
        canonical_display_name=None,
        size_description=None,
        specification=None,
        material_id=None,
        full_colly_count=1,
        qty_per_full_colly=Decimal("50"),
        partial_qty=Decimal("0"),
        total_qty=Decimal("50"),
        unit="sheet",
    )
    return ReceiptCandidateRequest(
        receipt_id=uuid.uuid4(),
        supplier_name="Supplier",
        document_number=None,
        document_date=None,
        received_at=datetime.now(timezone.utc),
        source_asset_reference=source or manifest_reference(),
        items=(item,),
    )


def review_view(request: ReceiptCandidateRequest, version: int = 1) -> ReceiptForReview:
    item = request.items[0]
    return ReceiptForReview(
        receipt_id=request.receipt_id,
        supplier_name=request.supplier_name,
        document_number=request.document_number,
        document_date=request.document_date,
        received_at=request.received_at,
        source_asset_reference=request.source_asset_reference,
        status=ReceiptStatus.NEEDS_REVIEW,
        version=version,
        confirmed_version=None,
        confirmed_at=None,
        confirmation_actor_reference=None,
        items=(
            ReceiptItemView(
                receipt_item_id=item.receipt_item_id,
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
                status=ReceiptStatus.NEEDS_REVIEW,
            ),
        ),
    )


class RecordingCandidatePort:
    def __init__(self, current: ReceiptForReview) -> None:
        self.current = current
        self.calls: list[tuple[object, ...]] = []

    async def create_candidate(self, request: ReceiptCandidateRequest) -> ReceiptForReview:
        self.calls.append(("create_candidate", request))
        return self.current

    async def revise_candidate(
        self, request: ReceiptCandidateRequest, expected_version: int
    ) -> ReceiptForReview:
        self.calls.append(("revise_candidate", request, expected_version))
        return self.current

    async def get_candidate_for_review(self, receipt_id: uuid.UUID) -> ReceiptForReview:
        self.calls.append(("get_candidate_for_review", receipt_id))
        return self.current


def async_test(function):
    def wrapper():
        return asyncio.run(function())

    return wrapper

def public_coroutines(cls: type) -> set[str]:
    return {
        name
        for name, member in inspect.getmembers(cls, inspect.iscoroutinefunction)
        if not name.startswith("_")
    }


def test_facade_and_port_expose_exactly_three_review_operations() -> None:
    expected = {"create_candidate", "revise_candidate", "get_candidate_for_review"}
    assert public_coroutines(ReviewFacade) == expected
    assert {
        name for name, value in CandidateReviewPort.__dict__.items()
        if inspect.isfunction(value) and not name.startswith("_")
    } == expected
    for prohibited in (
        "confirm_receipt",
        "post_confirmed_receipt",
        "get_repository",
        "execute",
        "execute_sql",
        "connection",
        "transaction",
    ):
        assert not hasattr(ReviewFacade, prohibited)
        assert not hasattr(CandidateReviewPort, prohibited)



@async_test
async def test_create_binds_exact_source_context_and_delegates() -> None:
    request = candidate_request()
    port = RecordingCandidatePort(review_view(request))
    facade = ReviewFacade(port)

    result = await facade.create_candidate(
        request, SourceContext(request.source_asset_reference, registry_record_id=7)
    )

    assert result == port.current
    assert port.calls == [("create_candidate", request)]



@async_test
async def test_create_rejects_conflicting_source_without_port_activity() -> None:
    request = candidate_request()
    port = RecordingCandidatePort(review_view(request))
    facade = ReviewFacade(port)

    with pytest.raises(ReviewApplicationError) as caught:
        await facade.create_candidate(request, SourceContext(manifest_reference()))

    assert caught.value.code is ReviewFailureCode.SOURCE_IDENTITY_CONFLICT
    assert port.calls == []



@async_test
async def test_revision_preserves_stored_source_and_expected_version() -> None:
    request = candidate_request()
    port = RecordingCandidatePort(review_view(request, version=3))
    facade = ReviewFacade(port)

    await facade.revise_candidate(request, 3, ActorContext("reviewer:7"))

    assert port.calls == [
        ("get_candidate_for_review", request.receipt_id),
        ("revise_candidate", request, 3),
    ]



@async_test
async def test_revision_rejects_source_override_before_mutation() -> None:
    request = candidate_request()
    existing_request = candidate_request(manifest_reference())
    existing = review_view(existing_request)
    existing = ReceiptForReview(
        receipt_id=request.receipt_id,
        supplier_name=existing.supplier_name,
        document_number=existing.document_number,
        document_date=existing.document_date,
        received_at=existing.received_at,
        source_asset_reference=existing.source_asset_reference,
        status=existing.status,
        version=existing.version,
        confirmed_version=existing.confirmed_version,
        confirmed_at=existing.confirmed_at,
        confirmation_actor_reference=existing.confirmation_actor_reference,
        items=existing.items,
    )
    port = RecordingCandidatePort(existing)

    with pytest.raises(ReviewApplicationError) as caught:
        await ReviewFacade(port).revise_candidate(
            request, 1, ActorContext("reviewer:7")
        )

    assert caught.value.code is ReviewFailureCode.SOURCE_IDENTITY_CONFLICT
    assert port.calls == [("get_candidate_for_review", request.receipt_id)]



@async_test
async def test_get_uses_actor_only_as_bounded_review_context() -> None:
    request = candidate_request()
    port = RecordingCandidatePort(review_view(request))

    result = await ReviewFacade(port).get_candidate_for_review(
        request.receipt_id, ActorContext("reviewer:7")
    )

    assert result == port.current
    assert port.calls == [("get_candidate_for_review", request.receipt_id)]


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "manifest:1",
        "/tmp/evidence.json",
        "//opt/aios/data/documents/manifests/00000000-0000-0000-0000-000000000000.json",
        "/opt/aios/data/documents/manifests/AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA.json",
        "/opt/aios/data/documents/manifests/not-a-uuid.json",
        "/opt/aios/data/documents/manifests/../evidence.json",
        "/opt/aios/data/documents/manifests/00000000-0000-0000-0000-000000000000.txt",
    ],
)
def test_source_context_rejects_missing_or_malformed_identity(value: str) -> None:
    with pytest.raises(ValueError):
        SourceContext(value)


def test_source_context_is_immutable_typed_and_minimal() -> None:
    context = SourceContext(manifest_reference(), registry_record_id=1)
    assert [field.name for field in fields(SourceContext)] == [
        "manifest_reference",
        "registry_record_id",
    ]
    with pytest.raises(FrozenInstanceError):
        context.manifest_reference = manifest_reference()  # type: ignore[misc]
    with pytest.raises(ValueError):
        SourceContext(manifest_reference(), registry_record_id=0)


def test_actor_context_is_immutable_typed_bounded_and_minimal() -> None:
    context = ActorContext("reviewer:7")
    assert [field.name for field in fields(ActorContext)] == ["actor_reference"]
    with pytest.raises(FrozenInstanceError):
        context.actor_reference = "changed"  # type: ignore[misc]
    for invalid in ("", " ", " reviewer", "reviewer\n7", "x" * 257):
        with pytest.raises(ValueError):
            ActorContext(invalid)


def test_contexts_have_no_authority_or_infrastructure_fields() -> None:
    prohibited = {
        "credential", "password", "token", "dsn", "sql", "repository",
        "factory", "connection", "environment", "metadata", "binary", "ocr",
        "brain", "telegram", "confirm", "post", "execute",
    }
    names = {field.name.lower() for cls in (SourceContext, ActorContext) for field in fields(cls)}
    assert all(not any(word in name for word in prohibited) for name in names)



@async_test
async def test_retrieval_fails_closed_on_malformed_persisted_source() -> None:
    request = candidate_request("asset:not-retained-manifest")
    facade = ReviewFacade(RecordingCandidatePort(review_view(request)))

    with pytest.raises(ReviewApplicationError) as caught:
        await facade.get_candidate_for_review(
            request.receipt_id, ActorContext("reviewer")
        )

    assert caught.value.code is ReviewFailureCode.SOURCE_IDENTITY_INVALID


@async_test
async def test_candidate_and_unexpected_errors_are_sanitized() -> None:
    request = candidate_request()

    class FailingPort(RecordingCandidatePort):
        async def create_candidate(self, request: ReceiptCandidateRequest) -> ReceiptForReview:
            raise MaterialReceiptError(MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR)

        async def get_candidate_for_review(self, receipt_id: uuid.UUID) -> ReceiptForReview:
            raise psycopg.OperationalError("password=secret dsn SQL SELECT")

    facade = ReviewFacade(FailingPort(review_view(request)))
    with pytest.raises(ReviewApplicationError) as candidate:
        await facade.create_candidate(request, SourceContext(request.source_asset_reference))
    assert str(candidate.value) == "CANDIDATE_OPERATION_FAILED"
    assert candidate.value.candidate_code is MaterialReceiptFailureCode.DATA_INTEGRITY_ERROR

    with pytest.raises(ReviewApplicationError) as unexpected:
        await facade.get_candidate_for_review(request.receipt_id, ActorContext("reviewer"))
    assert str(unexpected.value) == "INTERNAL_FAILURE"
    assert "secret" not in str(unexpected.value)
