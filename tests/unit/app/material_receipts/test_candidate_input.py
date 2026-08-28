from __future__ import annotations

from dataclasses import fields, FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
from stat import S_IFBLK, S_IFCHR, S_IFDIR, S_IFIFO, S_IFREG, S_IFSOCK
from uuid import UUID, uuid1, uuid4

import pytest

from core.app.input_classifier import InputType
from core.brain.inference_contracts import FailureCode, InferenceResult
from core.event import EventDeliveryFailureCode
from core.inventory_posting.repository import InventoryPostingRepository
from core.inventory_posting.service import InventoryPostingService
from core.material_receipts.repository import MaterialReceiptRepository
from core.material_receipts.service import MaterialReceiptService
from core.app.material_receipts import candidate_input
from core.app.material_receipts.candidate_input import (
    TrustedReceiptFacts,
    TrustedReceiptItemFacts,
    build_receipt_candidate_request,
    source_context_from_ingestion_result,
)
from core.app.material_receipts.candidate_input_errors import (
    CandidateInputError,
    CandidateInputFailureCode,
)
from core.app.material_receipts import review_use_cases
from core.ingestion.universal_ingestion import IngestionResult


def manifest_values(manifest_id: UUID) -> dict[str, object]:
    return {
        "manifest_id": str(manifest_id),
        "represented_media_type": "text",
        "received_at": "2026-08-27T00:00:00Z",
        "manifest_status": "created",
        "metadata": {"media_type": "text", "character_count": 1},
    }


@pytest.fixture
def retained_manifest(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "manifests"
    root.mkdir()
    monkeypatch.setattr(review_use_cases, "_MANIFEST_ROOT", root)
    identifier = uuid4()
    path = root / f"{identifier}.json"
    path.write_text(json.dumps(manifest_values(identifier)), encoding="utf-8")
    return path


def ingestion(path: Path, *, registered: bool = False, record_id=None) -> IngestionResult:
    return IngestionResult(
        input_type=InputType.TEXT,
        recognized_input_type=InputType.TEXT,
        stored_path=None,
        manifest_path=str(path),
        metadata={"untrusted": "ignored"},
        text="untrusted text",
        register_handoff_ready=True,
        process_handoff_ready=False,
        route_handoff_ready=False,
        respond_acknowledgement_ready=True,
        registration_succeeded=registered,
        registry_record_id=record_id,
        brain_result=None,
    )


def item(**overrides) -> TrustedReceiptItemFacts:
    values = {
        "line_number": 1,
        "candidate_material_description": "Steel sheet",
        "canonical_display_name": None,
        "size_description": None,
        "specification": None,
        "material_id": None,
        "full_colly_count": 2,
        "qty_per_full_colly": Decimal("50"),
        "partial_qty": Decimal("3"),
        "total_qty": Decimal("103"),
        "unit": "sheet",
    }
    values.update(overrides)
    return TrustedReceiptItemFacts(**values)


def facts(*items: TrustedReceiptItemFacts, **overrides) -> TrustedReceiptFacts:
    values = {
        "supplier_name": "PT Example",
        "document_number": "DO-31A",
        "document_date": date(2026, 8, 27),
        "received_at": datetime(2026, 8, 27, tzinfo=timezone.utc),
        "items": items or (item(),),
    }
    values.update(overrides)
    return TrustedReceiptFacts(**values)


def id_factory(*values: UUID):
    iterator = iter(values)
    return lambda: next(iterator)


def test_valid_evidence_and_facts_map_exactly(retained_manifest: Path) -> None:
    receipt_id, item_id = uuid4(), uuid4()
    trusted = facts()
    request = build_receipt_candidate_request(
        ingestion(retained_manifest), trusted, id_factory=id_factory(receipt_id, item_id)
    )

    assert request.receipt_id == receipt_id
    assert request.items[0].receipt_item_id == item_id
    assert request.source_asset_reference == str(retained_manifest)
    assert request.supplier_name == trusted.supplier_name
    assert request.items[0].total_qty is trusted.items[0].total_qty
    assert request.items[0].partial_qty is trusted.items[0].partial_qty
    with pytest.raises(FrozenInstanceError):
        request.supplier_name = "changed"


def test_registry_combinations(retained_manifest: Path) -> None:
    assert source_context_from_ingestion_result(
        ingestion(retained_manifest, registered=True, record_id=31)
    ).registry_record_id == 31
    assert source_context_from_ingestion_result(
        ingestion(retained_manifest, registered=False, record_id=None)
    ).registry_record_id is None
    invalid = (
        ingestion(retained_manifest, registered=False, record_id=31),
        ingestion(retained_manifest, registered=True, record_id=None),
        ingestion(retained_manifest, registered=True, record_id=0),
    )
    for evidence in invalid:
        with pytest.raises(CandidateInputError) as caught:
            source_context_from_ingestion_result(evidence)
        assert caught.value.code is CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE


def test_trusted_dtos_exclude_application_and_source_authority() -> None:
    receipt_fields = {field.name for field in fields(TrustedReceiptFacts)}
    item_fields = {field.name for field in fields(TrustedReceiptItemFacts)}
    assert not receipt_fields & {
        "receipt_id", "source_asset_reference", "manifest_reference", "registry_record_id"
    }
    assert "receipt_item_id" not in item_fields
    with pytest.raises(TypeError):
        facts(receipt_id=uuid4())
    with pytest.raises(TypeError):
        item(receipt_item_id=uuid4())


def test_ingestion_payload_has_no_business_fact_authority(retained_manifest: Path) -> None:
    evidence = ingestion(retained_manifest)
    evidence.metadata = {"supplier_name": "ATTACK", "total_qty": "999"}
    evidence.text = "supplier=ATTACK"
    request = build_receipt_candidate_request(evidence, facts())
    assert request.supplier_name == "PT Example"
    assert request.items[0].total_qty == Decimal("103")


def forge(cls, **values):
    value = object.__new__(cls)
    for name, field_value in values.items():
        object.__setattr__(value, name, field_value)
    return value


def test_forged_and_subclass_dtos_fail_before_manifest_or_ids(retained_manifest: Path, monkeypatch) -> None:
    manifest_calls = 0
    id_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError

    def forbidden_id():
        nonlocal id_calls
        id_calls += 1
        raise AssertionError

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    forged_item = forge(
        TrustedReceiptItemFacts,
        line_number=0,
        candidate_material_description=None,
        canonical_display_name=None,
        size_description=None,
        specification=None,
        material_id=None,
        full_colly_count=0,
        qty_per_full_colly=None,
        partial_qty=Decimal("0"),
        total_qty=Decimal("1"),
        unit="pcs",
    )
    forged_facts = forge(
        TrustedReceiptFacts,
        supplier_name="PT Example",
        document_number=None,
        document_date=None,
        received_at=datetime.now(timezone.utc),
        items=(forged_item,),
    )
    evidence = forge(
        IngestionResult,
        manifest_path="/bad",
        register_handoff_ready=True,
        registration_succeeded=False,
        registry_record_id=None,
    )
    for bad_evidence, bad_facts in ((evidence, facts()), (ingestion(retained_manifest), forged_facts)):
        with pytest.raises(CandidateInputError):
            build_receipt_candidate_request(bad_evidence, bad_facts, id_factory=forbidden_id)
    assert manifest_calls == 0
    assert id_calls == 0

    class FactsSubclass(TrustedReceiptFacts):
        pass

    subclass = object.__new__(FactsSubclass)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(evidence, subclass)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda path: path.unlink(),
        lambda path: path.write_text("{", encoding="utf-8"),
        lambda path: path.write_text("{}", encoding="utf-8"),
        lambda path: path.write_text(
            json.dumps(manifest_values(uuid4())), encoding="utf-8"
        ),
    ],
    ids=("nonexistent", "invalid-json", "schema-invalid", "id-mismatch"),
)
def test_invalid_manifest_content_fails_closed(retained_manifest: Path, mutator) -> None:
    mutator(retained_manifest)
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(ingestion(retained_manifest), facts())
    assert caught.value.code is CandidateInputFailureCode.RETAINED_MANIFEST_INVALID
    assert str(retained_manifest) not in str(caught.value)


def test_symlink_and_broken_symlink_are_rejected(
    retained_manifest: Path, monkeypatch
) -> None:
    target = retained_manifest
    link = target.parent / f"{uuid4()}.json"
    link.symlink_to(target)
    for path in (link,):
        with pytest.raises(CandidateInputError) as caught:
            build_receipt_candidate_request(ingestion(path), facts())
        assert caught.value.code is CandidateInputFailureCode.RETAINED_MANIFEST_INVALID
    target.unlink()
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(ingestion(link), facts())


@pytest.mark.parametrize("mode", [S_IFDIR, S_IFIFO, S_IFSOCK, S_IFCHR, S_IFBLK])
def test_nonregular_manifest_types_rejected(retained_manifest: Path, monkeypatch, mode) -> None:
    monkeypatch.setattr(
        candidate_input.os,
        "lstat",
        lambda path: type("Status", (), {"st_mode": mode})(),
    )
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(ingestion(retained_manifest), facts())
    assert caught.value.code is CandidateInputFailureCode.RETAINED_MANIFEST_INVALID


def test_directory_alternate_root_traversal_and_bad_name_rejected(
    retained_manifest: Path, tmp_path: Path
) -> None:
    paths = (
        retained_manifest.parent,
        tmp_path / retained_manifest.name,
        retained_manifest.parent / ".." / "manifests" / retained_manifest.name,
        retained_manifest.parent / "NOT-A-UUID.json",
    )
    for path in paths:
        evidence = ingestion(path)
        with pytest.raises(CandidateInputError) as caught:
            source_context_from_ingestion_result(evidence)
        assert caught.value.code is CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE


def test_generated_ids_are_v4_unique_and_deterministic(retained_manifest: Path) -> None:
    identifiers = (uuid4(), uuid4(), uuid4())
    request = build_receipt_candidate_request(
        ingestion(retained_manifest),
        facts(item(line_number=1), item(line_number=2)),
        id_factory=id_factory(*identifiers),
    )
    actual = (request.receipt_id,) + tuple(i.receipt_item_id for i in request.items)
    assert actual == identifiers
    assert all(type(value) is UUID and value.version == 4 for value in actual)


@pytest.mark.parametrize("bad", ["id", uuid1()])
def test_bad_id_factory_output_rejected(retained_manifest: Path, bad) -> None:
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(
            ingestion(retained_manifest), facts(), id_factory=lambda: bad
        )
    assert caught.value.code is CandidateInputFailureCode.ID_GENERATION_INVALID


def test_duplicate_ids_including_receipt_item_reuse_rejected(retained_manifest: Path) -> None:
    duplicate = uuid4()
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(
            ingestion(retained_manifest),
            facts(),
            id_factory=id_factory(duplicate, duplicate),
        )
    assert caught.value.code is CandidateInputFailureCode.ID_GENERATION_INVALID


def test_item_count_boundaries(retained_manifest: Path) -> None:
    with pytest.raises(CandidateInputError):
        facts(items=())
    five_hundred = tuple(item(line_number=index) for index in range(1, 501))
    request = build_receipt_candidate_request(
        ingestion(retained_manifest), facts(*five_hundred)
    )
    assert len(request.items) == 500
    with pytest.raises(CandidateInputError) as caught:
        facts(*(item(line_number=index) for index in range(1, 502)))
    assert caught.value.code is CandidateInputFailureCode.LIMIT_EXCEEDED


@pytest.mark.parametrize(
    "overrides,code",
    [
        ({"line_number": 0}, CandidateInputFailureCode.TRUSTED_FACTS_INVALID),
        ({"full_colly_count": -1}, CandidateInputFailureCode.TRUSTED_FACTS_INVALID),
        ({"full_colly_count": 1_000_001}, CandidateInputFailureCode.LIMIT_EXCEEDED),
        ({"qty_per_full_colly": None}, CandidateInputFailureCode.TRUSTED_FACTS_INVALID),
        (
            {"full_colly_count": 0, "qty_per_full_colly": Decimal("1"), "total_qty": Decimal("3")},
            CandidateInputFailureCode.TRUSTED_FACTS_INVALID,
        ),
        ({"qty_per_full_colly": Decimal("1000001")}, CandidateInputFailureCode.LIMIT_EXCEEDED),
        ({"partial_qty": Decimal("-1")}, CandidateInputFailureCode.TRUSTED_FACTS_INVALID),
        ({"partial_qty": Decimal("1000000001")}, CandidateInputFailureCode.LIMIT_EXCEEDED),
        ({"total_qty": Decimal("0")}, CandidateInputFailureCode.TRUSTED_FACTS_INVALID),
        ({"total_qty": Decimal("1000000001")}, CandidateInputFailureCode.LIMIT_EXCEEDED),
        ({"partial_qty": Decimal("0.0000001")}, CandidateInputFailureCode.DECIMAL_POLICY_INVALID),
        ({"partial_qty": Decimal("123456789012345678901")}, CandidateInputFailureCode.DECIMAL_POLICY_INVALID),
        ({"partial_qty": 3.0}, CandidateInputFailureCode.DECIMAL_POLICY_INVALID),
        ({"partial_qty": Decimal("NaN")}, CandidateInputFailureCode.DECIMAL_POLICY_INVALID),
        ({"partial_qty": Decimal("Infinity")}, CandidateInputFailureCode.DECIMAL_POLICY_INVALID),
    ],
)
def test_quantity_policy_rejections(overrides, code) -> None:
    with pytest.raises(CandidateInputError) as caught:
        item(**overrides)
    assert caught.value.code is code


def test_approved_numeric_upper_bounds() -> None:
    value = item(
        full_colly_count=1_000_000,
        qty_per_full_colly=Decimal("1000"),
        partial_qty=Decimal("0"),
        total_qty=Decimal("1000000000"),
        unit="pcs",
    )
    assert value.total_qty == Decimal("1000000000")
    per_colly = item(
        full_colly_count=1,
        qty_per_full_colly=Decimal("1000000"),
        partial_qty=Decimal("0"),
        total_qty=Decimal("1000000"),
        unit="pcs",
    )
    assert per_colly.qty_per_full_colly == Decimal("1000000")
    zero_colly = item(
        full_colly_count=0,
        qty_per_full_colly=None,
        partial_qty=Decimal("1000000000"),
        total_qty=Decimal("1000000000"),
        unit="pcs",
    )
    assert zero_colly.partial_qty == Decimal("1000000000")


@pytest.mark.parametrize(
    "field,value",
    [
        ("supplier_name", ""),
        ("supplier_name", " supplier"),
        ("supplier_name", "x" * 129),
        ("document_number", ""),
        ("document_number", "x" * 129),
    ],
)
def test_receipt_text_policy(field, value) -> None:
    with pytest.raises(CandidateInputError):
        facts(**{field: value})


@pytest.mark.parametrize(
    "value", ["", " description", "x" * 513]
)
def test_description_text_policy(value) -> None:
    with pytest.raises(CandidateInputError):
        item(candidate_material_description=value)


def test_scale_six_decimal_is_preserved_without_rounding() -> None:
    exact = Decimal("0.123456")
    value = item(
        full_colly_count=0,
        qty_per_full_colly=None,
        partial_qty=exact,
        total_qty=exact,
        unit="kg",
    )
    assert value.partial_qty is exact
    assert value.total_qty is exact



def test_packaging_examples_exact_decimal_and_units() -> None:
    first = item(
        full_colly_count=125,
        qty_per_full_colly=Decimal("50"),
        partial_qty=Decimal("0"),
        total_qty=Decimal("6250"),
    )
    second = item(
        full_colly_count=62,
        qty_per_full_colly=Decimal("50"),
        partial_qty=Decimal("38"),
        total_qty=Decimal("3138"),
    )
    assert (first.total_qty, second.total_qty) == (Decimal("6250"), Decimal("3138"))
    with pytest.raises(CandidateInputError) as mismatch:
        item(total_qty=Decimal("104"))
    assert mismatch.value.code is CandidateInputFailureCode.PACKAGING_FORMULA_INVALID
    with pytest.raises(CandidateInputError):
        item(
            full_colly_count=0,
            qty_per_full_colly=None,
            partial_qty=Decimal("1.5"),
            total_qty=Decimal("1.5"),
        )
    for unit in ("SHEET", "Sheet", "piece"):
        with pytest.raises(CandidateInputError):
            item(unit=unit)


def test_time_policy() -> None:
    assert facts().received_at.utcoffset() is not None
    with pytest.raises(CandidateInputError):
        facts(received_at=datetime(2026, 8, 27))


def test_duplicate_lines_rejected() -> None:
    with pytest.raises(CandidateInputError):
        facts(item(line_number=1), item(line_number=1))


def test_import_surface_has_no_persistence_or_runtime_capability() -> None:
    source = Path(candidate_input.__file__).read_text(encoding="utf-8")
    prohibited = (
        "MaterialReceiptRepository",
        "InventoryPostingRepository",
        "from_environment",
        "create_candidate(",
        "confirm_receipt",
        "post_confirmed_receipt",
        "psycopg",
        "core.adapters.telegram",
        "core.registry",
        "core.brain",
        "os.environ",
    )
    assert not [token for token in prohibited if token in source]


def test_manifest_file_is_opened_without_following_symlinks(
    retained_manifest: Path, monkeypatch
) -> None:
    real_open = candidate_input.os.open
    observed_flags = []

    def recording_open(path, flags):
        observed_flags.append(flags)
        return real_open(path, flags)

    monkeypatch.setattr(candidate_input.os, "open", recording_open)
    build_receipt_candidate_request(ingestion(retained_manifest), facts())
    if hasattr(os, "O_NOFOLLOW"):
        assert observed_flags[0] & os.O_NOFOLLOW


def inference_result() -> InferenceResult:
    return InferenceResult(
        schema_version=1,
        correlation_id="corr-stage-031a",
        request_id="request-stage-031a",
        success=False,
        failure_code=FailureCode.RUNTIME_UNAVAILABLE,
        structured_output=None,
        provider_id=None,
        model_id=None,
        duration_ms=0,
    )


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("input_type", "text"),
        ("recognized_input_type", object()),
        ("stored_path", 1),
        ("manifest_path", None),
        ("metadata", ()),
        ("text", b"text"),
        ("register_handoff_ready", 1),
        ("process_handoff_ready", True),
        ("route_handoff_ready", 1),
        ("respond_acknowledgement_ready", False),
        ("registration_succeeded", 1),
        ("registry_record_id", 1),
        ("event_publication_attempted", 1),
        ("event_delivery_succeeded", 1),
        ("event_delivery_failure_code", "no_handler"),
        ("brain_result", object()),
    ],
)
def test_mutated_exact_ingestion_fields_fail_before_manifest_and_ids(
    retained_manifest: Path, monkeypatch, field_name: str, bad_value: object
) -> None:
    evidence = ingestion(retained_manifest)
    object.__setattr__(evidence, field_name, bad_value)
    manifest_calls = 0
    id_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("manifest access must be unreachable")

    def forbidden_id():
        nonlocal id_calls
        id_calls += 1
        raise AssertionError("ID generation must be unreachable")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(evidence, facts(), id_factory=forbidden_id)
    assert caught.value.code is CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE
    assert manifest_calls == 0
    assert id_calls == 0


@pytest.mark.parametrize(
    "updates",
    [
        {"registration_succeeded": True, "registry_record_id": None},
        {"registration_succeeded": False, "registry_record_id": 31},
        {"event_publication_attempted": False, "event_delivery_succeeded": True},
        {
            "event_publication_attempted": False,
            "event_delivery_failure_code": EventDeliveryFailureCode.NO_HANDLER,
        },
        {
            "registration_succeeded": True,
            "registry_record_id": 31,
            "event_publication_attempted": True,
            "event_delivery_succeeded": True,
            "event_delivery_failure_code": EventDeliveryFailureCode.NO_HANDLER,
        },
        {
            "registration_succeeded": True,
            "registry_record_id": 31,
            "event_publication_attempted": True,
            "event_delivery_succeeded": False,
            "event_delivery_failure_code": None,
        },
        {"route_handoff_ready": True},
        {"brain_result": inference_result()},
    ],
)
def test_forged_ingestion_relationships_fail_before_manifest(
    retained_manifest: Path, monkeypatch, updates: dict[str, object]
) -> None:
    evidence = ingestion(retained_manifest)
    for name, value in updates.items():
        object.__setattr__(evidence, name, value)
    manifest_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("manifest access must be unreachable")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(evidence, facts())
    assert manifest_calls == 0


def test_valid_event_state_is_accepted_and_brain_result_is_fail_closed(
    retained_manifest: Path, monkeypatch,
) -> None:
    failed_delivery = ingestion(retained_manifest, registered=True, record_id=31)
    failed_delivery.event_publication_attempted = True
    failed_delivery.event_delivery_failure_code = EventDeliveryFailureCode.NO_HANDLER
    assert source_context_from_ingestion_result(failed_delivery).registry_record_id == 31

    with_brain = ingestion(retained_manifest, registered=True, record_id=31)
    with_brain.event_publication_attempted = True
    with_brain.event_delivery_succeeded = True
    with_brain.route_handoff_ready = True
    with_brain.brain_result = inference_result()
    manifest_calls = 0
    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("Brain-bearing evidence must fail before manifest access")
    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(with_brain, facts())
    assert manifest_calls == 0



def test_forged_exact_inference_result_is_revalidated_before_manifest(
    retained_manifest: Path, monkeypatch
) -> None:
    brain = inference_result()
    object.__setattr__(brain, "success", True)
    evidence = ingestion(retained_manifest, registered=True, record_id=31)
    evidence.event_publication_attempted = True
    evidence.event_delivery_succeeded = True
    evidence.route_handoff_ready = True
    evidence.brain_result = brain
    manifest_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("manifest access must be unreachable")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(evidence, facts())
    assert manifest_calls == 0


@pytest.mark.parametrize("control", ["\n", "\r", "\t", "\x00", "\x01", "\x7f", "\x85"])
@pytest.mark.parametrize(
    "field_name",
    [
        "candidate_material_description",
        "canonical_display_name",
        "size_description",
        "specification",
    ],
)
def test_descriptive_text_rejects_embedded_controls(
    field_name: str, control: str
) -> None:
    with pytest.raises(CandidateInputError):
        item(**{field_name: f"valid{control}text"})


@pytest.mark.parametrize("control", ["\n", "\r", "\t", "\x00", "\x01", "\x7f", "\x85"])
@pytest.mark.parametrize("field_name", ["supplier_name", "document_number"])
def test_receipt_text_rejects_embedded_controls(
    field_name: str, control: str
) -> None:
    with pytest.raises(CandidateInputError):
        facts(**{field_name: f"valid{control}text"})


def test_text_exact_limits_and_unicode_are_preserved() -> None:
    supplier = "供" * 128
    document = "é" * 128
    description = "鋼" * 512
    trusted = facts(
        supplier_name=supplier,
        document_number=document,
        items=(item(candidate_material_description=description),),
    )
    assert trusted.supplier_name == supplier
    assert trusted.document_number == document
    assert trusted.items[0].candidate_material_description == description
    with pytest.raises(CandidateInputError):
        facts(supplier_name="供" * 129)
    with pytest.raises(CandidateInputError):
        facts(document_number="é" * 129)
    with pytest.raises(CandidateInputError):
        item(candidate_material_description="鋼" * 513)


def test_all_trusted_dto_subclasses_and_forged_source_context_fail(
    retained_manifest: Path, monkeypatch
) -> None:
    class ItemSubclass(TrustedReceiptItemFacts):
        pass

    class EvidenceSubclass(IngestionResult):
        pass

    item_subclass = object.__new__(ItemSubclass)
    forged_facts = forge(
        TrustedReceiptFacts,
        supplier_name="PT Example",
        document_number=None,
        document_date=None,
        received_at=datetime.now(timezone.utc),
        items=(item_subclass,),
    )
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(ingestion(retained_manifest), forged_facts)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(object.__new__(EvidenceSubclass), facts())

    context = object.__new__(review_use_cases.SourceContext)
    object.__setattr__(context, "manifest_reference", "/bad")
    object.__setattr__(context, "registry_record_id", None)
    lstat_calls = 0

    def forbidden_lstat(path):
        nonlocal lstat_calls
        lstat_calls += 1
        raise AssertionError("forged context must fail first")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(ValueError):
        candidate_input._verified_manifest_id(context)
    assert lstat_calls == 0


def test_item_to_item_generated_id_collision_is_rejected(retained_manifest: Path) -> None:
    receipt_id, duplicate = uuid4(), uuid4()
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(
            ingestion(retained_manifest),
            facts(item(line_number=1), item(line_number=2)),
            id_factory=id_factory(receipt_id, duplicate, duplicate),
        )
    assert caught.value.code is CandidateInputFailureCode.ID_GENERATION_INVALID


def test_invalid_input_has_zero_operational_capability(
    retained_manifest: Path, monkeypatch
) -> None:
    import psycopg

    calls = {name: 0 for name in (
        "material_repository", "posting_repository", "db", "persist",
        "confirm", "post", "candidate_credentials", "posting_credentials",
    )}

    def forbidden(name):
        def call(*args, **kwargs):
            calls[name] += 1
            raise AssertionError(f"{name} must be unreachable")
        return call

    monkeypatch.setattr(
        MaterialReceiptRepository, "__init__", forbidden("material_repository")
    )
    monkeypatch.setattr(
        InventoryPostingRepository, "__init__", forbidden("posting_repository")
    )
    monkeypatch.setattr(
        MaterialReceiptRepository, "_create_receipt_candidate", forbidden("persist")
    )
    monkeypatch.setattr(
        MaterialReceiptService, "confirm_receipt", forbidden("confirm")
    )
    monkeypatch.setattr(
        InventoryPostingService, "post_confirmed_receipt", forbidden("post")
    )
    monkeypatch.setattr(
        MaterialReceiptRepository,
        "from_environment",
        forbidden("candidate_credentials"),
    )
    monkeypatch.setattr(
        InventoryPostingRepository,
        "from_environment",
        forbidden("posting_credentials"),
    )
    monkeypatch.setattr(psycopg, "connect", forbidden("db"))
    monkeypatch.setattr(psycopg.Connection, "connect", forbidden("db"))
    monkeypatch.setattr(psycopg.AsyncConnection, "connect", forbidden("db"))

    evidence = ingestion(retained_manifest)
    object.__setattr__(evidence, "brain_result", object())
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(evidence, facts())
    assert calls == {name: 0 for name in calls}

def test_default_factory_generates_unique_uuid4_values(retained_manifest: Path) -> None:
    request = build_receipt_candidate_request(
        ingestion(retained_manifest),
        facts(item(line_number=1), item(line_number=2)),
    )
    identifiers = (request.receipt_id,) + tuple(
        receipt_item.receipt_item_id for receipt_item in request.items
    )
    assert len(set(identifiers)) == 3
    assert all(type(identifier) is UUID and identifier.version == 4 for identifier in identifiers)


@pytest.mark.parametrize("failure", [None, True, 4.0, lambda: (_ for _ in ()).throw(RuntimeError())])
def test_additional_bad_id_factories_are_bounded(
    retained_manifest: Path, failure
) -> None:
    factory = failure if callable(failure) else lambda: failure
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(
            ingestion(retained_manifest), facts(), id_factory=factory
        )
    assert caught.value.code is CandidateInputFailureCode.ID_GENERATION_INVALID


def test_post_construction_dto_mutation_fails_before_manifest_and_ids(
    retained_manifest: Path, monkeypatch
) -> None:
    trusted_item = item()
    trusted = facts(trusted_item)
    object.__setattr__(trusted_item, "total_qty", Decimal("104"))
    manifest_calls = 0
    id_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("manifest access must be unreachable")

    def forbidden_id():
        nonlocal id_calls
        id_calls += 1
        raise AssertionError("ID generation must be unreachable")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(
            ingestion(retained_manifest), trusted, id_factory=forbidden_id
        )
    assert manifest_calls == 0
    assert id_calls == 0


def test_numeric_exact_boundaries_and_representations() -> None:
    one_item = item(
        full_colly_count=1,
        qty_per_full_colly=Decimal("0.000001"),
        partial_qty=Decimal("0"),
        total_qty=Decimal("0.000001"),
        unit="kg",
    )
    assert one_item.qty_per_full_colly == Decimal("0.000001")
    assert item(
        full_colly_count=0,
        qty_per_full_colly=None,
        partial_qty=Decimal("1E+3"),
        total_qty=Decimal("1E+3"),
        unit="kg",
    ).total_qty == Decimal("1E+3")
    trailing = Decimal("1.000000")
    preserved = item(
        full_colly_count=0,
        qty_per_full_colly=None,
        partial_qty=trailing,
        total_qty=trailing,
        unit="kg",
    )
    assert preserved.partial_qty is trailing
    with pytest.raises(CandidateInputError):
        item(partial_qty=Decimal("sNaN"))
    with pytest.raises(CandidateInputError):
        item(partial_qty=Decimal("-Infinity"))


def test_packaging_smallest_supported_mismatch_fails() -> None:
    with pytest.raises(CandidateInputError) as caught:
        item(total_qty=Decimal("103.000001"), unit="kg")
    assert caught.value.code is CandidateInputFailureCode.PACKAGING_FORMULA_INVALID


@pytest.mark.parametrize(
    "bad_unit",
    ["SHEET", "Sheet", "piece", "pieces", "kgs", "Roll", "PACK", " sheet", "sheet ", "ѕheet"],
)
def test_complete_invalid_unit_vocabulary(bad_unit: str) -> None:
    with pytest.raises(CandidateInputError):
        item(unit=bad_unit)


def test_timezone_with_none_or_raising_offset_is_rejected() -> None:
    from datetime import timedelta, tzinfo

    class NoneTimezone(tzinfo):
        def utcoffset(self, dt):
            return None

    class RaisingTimezone(tzinfo):
        def utcoffset(self, dt):
            raise RuntimeError("forged timezone")

    for zone in (NoneTimezone(), RaisingTimezone()):
        with pytest.raises(CandidateInputError):
            facts(received_at=datetime(2026, 8, 27, tzinfo=zone))
    assert facts(
        received_at=datetime(2026, 8, 27, tzinfo=timezone(timedelta(hours=7)))
    ).received_at.utcoffset() == timedelta(hours=7)


def test_actual_fifo_and_socket_manifests_are_rejected(
    retained_manifest: Path, monkeypatch,
) -> None:
    import socket

    retained_manifest.unlink()
    os.mkfifo(retained_manifest)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(ingestion(retained_manifest), facts())
    retained_manifest.unlink()
    short_socket_path = Path("/tmp") / f"{uuid4()}.json"
    monkeypatch.setattr(review_use_cases, "_MANIFEST_ROOT", Path("/tmp"))
    unix_socket = socket.socket(socket.AF_UNIX)
    try:
        unix_socket.bind(str(short_socket_path))
        with pytest.raises(CandidateInputError):
            build_receipt_candidate_request(ingestion(short_socket_path), facts())
    finally:
        unix_socket.close()
        short_socket_path.unlink(missing_ok=True)


def test_import_and_mapper_construction_have_no_operational_side_effects(
    tmp_path: Path, monkeypatch
) -> None:
    import importlib
    import psycopg

    before_environment = dict(os.environ)
    before_files = tuple(tmp_path.iterdir())
    calls = 0

    def forbidden(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("operational capability must be unreachable")

    monkeypatch.setattr(psycopg, "connect", forbidden)
    monkeypatch.setattr(psycopg.Connection, "connect", forbidden)
    monkeypatch.setattr(psycopg.AsyncConnection, "connect", forbidden)
    monkeypatch.setattr(MaterialReceiptRepository, "from_environment", forbidden)
    monkeypatch.setattr(InventoryPostingRepository, "from_environment", forbidden)
    imported = importlib.import_module(candidate_input.__name__)
    assert calls == 0
    assert dict(os.environ) == before_environment
    assert tuple(tmp_path.iterdir()) == before_files
    assert imported.build_receipt_candidate_request is not None

@pytest.mark.parametrize("bad_code", ["no_handler", 1, object()])
def test_attempted_failed_delivery_requires_exact_failure_enum_before_manifest(
    retained_manifest: Path, monkeypatch, bad_code: object
) -> None:
    evidence = ingestion(retained_manifest, registered=True, record_id=31)
    evidence.event_publication_attempted = True
    evidence.event_delivery_succeeded = False
    object.__setattr__(evidence, "event_delivery_failure_code", bad_code)
    manifest_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("invalid event code must fail before manifest access")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError) as caught:
        build_receipt_candidate_request(evidence, facts())
    assert caught.value.code is CandidateInputFailureCode.INVALID_INGESTION_EVIDENCE
    assert manifest_calls == 0


def test_fully_forged_exact_ingestion_result_revalidates_every_current_field(
    retained_manifest: Path, monkeypatch
) -> None:
    original = ingestion(retained_manifest)
    forged = object.__new__(IngestionResult)
    for field in fields(IngestionResult):
        object.__setattr__(forged, field.name, getattr(original, field.name))
    object.__setattr__(forged, "metadata", object())
    manifest_calls = 0

    def forbidden_lstat(path):
        nonlocal manifest_calls
        manifest_calls += 1
        raise AssertionError("forged evidence must fail before manifest access")

    monkeypatch.setattr(candidate_input.os, "lstat", forbidden_lstat)
    with pytest.raises(CandidateInputError):
        build_receipt_candidate_request(forged, facts())
    assert manifest_calls == 0
