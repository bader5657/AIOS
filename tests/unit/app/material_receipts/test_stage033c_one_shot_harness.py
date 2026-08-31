from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import threading
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

from core.app.material_receipts import stage033c_one_shot_harness as harness
from core.app.material_receipts.candidate_create_authorization import (
    CandidateCreateControlError,
    CandidateCreateControlFailureCode,
)
from core.app.material_receipts.candidate_input_errors import (
    CandidateInputError,
    CandidateInputFailureCode,
)
from core.app.material_receipts.results import ReviewApplicationError, ReviewFailureCode
from core.material_receipts.models import ReceiptForReview, ReceiptItemView, ReceiptStatus


RESULT_FIELDS = {
    "schema_version",
    "outcome",
    "receipt_id",
    "status",
    "source_manifest_reference",
    "version",
    "confirmed_version",
    "item_count",
    "input_sha256",
    "harness_sha256",
    "exit_classification",
    "exit_code",
    "error_classification",
    "message",
}


@pytest.fixture(autouse=True)
def reset_one_shot_state(monkeypatch):
    monkeypatch.setattr(harness, "_state", harness._UNUSED)


def valid_value() -> dict[str, object]:
    return {
        "schema_version": "aios-stage-0.33c-one-shot-input-v1",
        "ingestion_result": {
            "input_type": "text",
            "recognized_input_type": "text",
            "stored_path": None,
            "manifest_path": (
                "/opt/aios/data/documents/manifests/"
                "550e8400-e29b-41d4-a716-446655440000.json"
            ),
            "metadata": {},
            "text": "",
            "register_handoff_ready": True,
            "process_handoff_ready": False,
            "route_handoff_ready": False,
            "respond_acknowledgement_ready": True,
            "registration_succeeded": False,
            "registry_record_id": None,
            "event_publication_attempted": False,
            "event_delivery_succeeded": False,
            "event_delivery_failure_code": None,
            "brain_result": None,
        },
        "trusted_receipt_facts": {
            "supplier_name": "PT Example",
            "document_number": "DO-1",
            "document_date": "2026-08-31",
            "received_at": "2026-08-31T12:34:56.123456Z",
            "items": [
                {
                    "line_number": 1,
                    "candidate_material_description": "Steel",
                    "canonical_display_name": None,
                    "size_description": None,
                    "specification": None,
                    "material_id": None,
                    "full_colly_count": 1,
                    "qty_per_full_colly": "50",
                    "partial_qty": "0",
                    "total_qty": "50",
                    "unit": "sheet",
                }
            ],
        },
    }


def transport(value: dict[str, object]) -> tuple[bytes, str]:
    semantic = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return semantic + b"\n", hashlib.sha256(semantic).hexdigest()


def result() -> ReceiptForReview:
    item = ReceiptItemView(
        UUID("650e8400-e29b-41d4-a716-446655440000"),
        1,
        "Steel",
        None,
        None,
        None,
        None,
        1,
        Decimal("50"),
        Decimal("0"),
        Decimal("50"),
        "sheet",
        ReceiptStatus.NEEDS_REVIEW,
    )
    return ReceiptForReview(
        UUID("750e8400-e29b-41d4-a716-446655440000"),
        "PT Example",
        "DO-1",
        date(2026, 8, 31),
        datetime(2026, 8, 31, tzinfo=timezone.utc),
        "/opt/aios/data/documents/manifests/550e8400-e29b-41d4-a716-446655440000.json",
        ReceiptStatus.NEEDS_REVIEW,
        1,
        None,
        None,
        None,
        (item,),
    )


def decoded(payload: bytes) -> dict[str, object]:
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    assert len(payload) <= harness.MAX_OUTPUT_BYTES
    semantic = payload[:-1]
    value = json.loads(semantic)
    assert harness._canonical_json(value) == semantic
    assert set(value) == RESULT_FIELDS
    return value


@pytest.mark.asyncio
async def test_success_is_observable_only_canonical_and_bounded(monkeypatch) -> None:
    calls = 0

    async def fake(request):
        nonlocal calls
        calls += 1
        assert type(request).__name__ == "ControlledCandidateCreateRequest"
        return result()

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fake)
    raw, digest = transport(valid_value())
    code, payload = await harness._execute_transport(raw, digest)
    value = decoded(payload)
    assert code == value["exit_code"] == 0
    assert value["receipt_id"] == "750e8400-e29b-41d4-a716-446655440000"
    assert value["status"] == "NEEDS_REVIEW"
    assert value["version"] == 1
    assert value["confirmed_version"] is None
    assert value["item_count"] == 1
    assert value["input_sha256"] == digest
    assert calls == 1
    prohibited = {
        "correlation_id",
        "consumed_at_utc",
        "authorization_path",
        "actor_reference",
        "transaction",
        "repository",
        "row_effects",
        "evidence_events",
        "supplier_name",
        "document_number",
        "quantities",
    }
    assert prohibited.isdisjoint(value)


@pytest.mark.asyncio
async def test_irreversible_claim_rejects_second_attempt_before_callable(monkeypatch) -> None:
    calls = 0

    async def fake(_request):
        nonlocal calls
        calls += 1
        return result()

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fake)
    raw, digest = transport(valid_value())
    first_code, _ = await harness._execute_transport(raw, digest)
    second_code, second_payload = await harness._execute_transport(raw, digest)
    assert first_code == 0
    assert second_code == 70
    assert decoded(second_payload)["error_classification"] == "HARNESS_INTERNAL_FAILURE"
    assert harness._state == harness._CLAIMED
    assert calls == 1


def test_atomic_claim_allows_exactly_one_concurrent_callable(monkeypatch) -> None:
    calls = 0
    calls_lock = threading.Lock()
    start = threading.Barrier(4)

    async def fake(_request):
        nonlocal calls
        with calls_lock:
            calls += 1
        return result()

    def invoke(raw: bytes, digest: str) -> int:
        start.wait(timeout=5)
        code, _ = asyncio.run(harness._execute_transport(raw, digest))
        return code

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fake)
    raw, digest = transport(valid_value())
    with ThreadPoolExecutor(max_workers=4) as executor:
        codes = list(executor.map(lambda _: invoke(raw, digest), range(4)))

    assert calls == 1
    assert codes.count(0) == 1
    assert codes.count(70) == 3
    assert harness._state == harness._CLAIMED


def test_paused_winner_rejects_loser_before_callable(monkeypatch) -> None:
    calls = 0
    winner_entered = threading.Event()
    release_winner = threading.Event()

    async def fake(_request):
        nonlocal calls
        calls += 1
        winner_entered.set()
        assert release_winner.wait(timeout=5)
        return result()

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fake)
    raw, digest = transport(valid_value())
    with ThreadPoolExecutor(max_workers=2) as executor:
        winner = executor.submit(asyncio.run, harness._execute_transport(raw, digest))
        assert winner_entered.wait(timeout=5)
        loser = executor.submit(asyncio.run, harness._execute_transport(raw, digest))
        loser_code, _ = loser.result(timeout=5)
        assert calls == 1
        assert loser_code == 70
        release_winner.set()
        winner_code, _ = winner.result(timeout=5)

    assert winner_code == 0
    assert calls == 1


@pytest.mark.asyncio
async def test_failed_winner_does_not_release_claim(monkeypatch) -> None:
    calls = 0

    async def fail(_request):
        nonlocal calls
        calls += 1
        raise RuntimeError("password=must-not-escape")

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fail)
    raw, digest = transport(valid_value())
    winner_code, winner_payload = await harness._execute_transport(raw, digest)
    loser_code, _ = await harness._execute_transport(raw, digest)

    assert winner_code == 70
    assert b"password=" not in winner_payload
    assert loser_code == 70
    assert harness._state == harness._CLAIMED
    assert calls == 1


@pytest.mark.asyncio
async def test_joint_decimal_witness_constructs_exact_decimal_dtos(monkeypatch) -> None:
    current = valid_value()
    item = current["trusted_receipt_facts"]["items"][0]
    item.update(
        full_colly_count=100,
        qty_per_full_colly="999999.999999",
        partial_qty="800000000.000001",
        total_qty="899999999.999901",
        unit="pack",
    )

    async def fake(request):
        actual = request.trusted_receipt_facts.items[0]
        assert actual.qty_per_full_colly == Decimal("999999.999999")
        assert actual.partial_qty == Decimal("800000000.000001")
        assert actual.total_qty == Decimal("899999999.999901")
        return result()

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fake)
    raw, digest = transport(current)
    code, _ = await harness._execute_transport(raw, digest)
    assert code == 0


@pytest.mark.asyncio
async def test_hash_mismatch_and_noncanonical_json_reject_before_call(monkeypatch) -> None:
    calls = 0

    async def forbidden(_request):
        nonlocal calls
        calls += 1

    monkeypatch.setattr(harness, "controlled_create_review_candidate", forbidden)
    raw, digest = transport(valid_value())
    wrong = "0" * 64 if digest != "0" * 64 else "1" * 64
    code, _ = await harness._execute_transport(raw, wrong)
    assert code == 40
    semantic = json.dumps(valid_value(), ensure_ascii=False).encode()
    code, _ = await harness._execute_transport(
        semantic + b"\n", hashlib.sha256(semantic).hexdigest()
    )
    assert code == 40
    assert calls == 0


def invalid_values() -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    current = valid_value()
    current["unknown"] = True
    values.append(current)
    current = valid_value()
    current["ingestion_result"]["metadata"] = {"arbitrary": "value"}
    values.append(current)
    current = valid_value()
    current["trusted_receipt_facts"]["items"] = []
    values.append(current)
    current = valid_value()
    template = current["trusted_receipt_facts"]["items"][0]
    current["trusted_receipt_facts"]["items"] = [
        {**template, "line_number": number} for number in range(1, 502)
    ]
    values.append(current)
    for key in ("raw_bytes", "document_content", "base64_content"):
        current = valid_value()
        current["trusted_receipt_facts"][key] = "AAECAw=="
        values.append(current)
    for spelling in (
        "01",
        "+1",
        "1e0",
        "1.0",
        "1.",
        "-0",
        "0.0000001",
        "123456789012345678901",
    ):
        current = valid_value()
        item = current["trusted_receipt_facts"]["items"][0]
        item["qty_per_full_colly"] = spelling
        values.append(current)
    current = valid_value()
    current["trusted_receipt_facts"]["items"][0]["partial_qty"] = 0
    values.append(current)
    return values


@pytest.mark.asyncio
@pytest.mark.parametrize("value", invalid_values())
async def test_closed_schema_and_noncanonical_values_reject_without_call(
    monkeypatch, value
) -> None:
    calls = 0

    async def forbidden(_request):
        nonlocal calls
        calls += 1
        raise AssertionError

    monkeypatch.setattr(harness, "controlled_create_review_candidate", forbidden)
    raw, digest = transport(value)
    code, payload = await harness._execute_transport(raw, digest)
    assert code == 40
    assert decoded(payload)["error_classification"] == "HARNESS_INPUT_VALIDATION_REJECTED"
    assert calls == 0
    assert harness._state == harness._UNUSED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw",
    [
        b"\xff\n",
        b'{"schema_version":"x","schema_version":"y"}\n',
        b"{}",
        b"{}\n\n",
        b"a" * harness.MAX_TRANSPORT_INPUT_BYTES + b"\n",
    ],
)
async def test_transport_utf8_duplicate_lf_and_size_rejections(monkeypatch, raw) -> None:
    async def forbidden(_request):
        raise AssertionError

    monkeypatch.setattr(harness, "controlled_create_review_candidate", forbidden)
    digest = hashlib.sha256(raw[:-1]).hexdigest()
    code, payload = await harness._execute_transport(raw, digest)
    assert code == 40
    assert decoded(payload)["exit_code"] == 40
    assert harness._state == harness._UNUSED


CONTROL_CASES = [
    (CandidateCreateControlFailureCode.AUTHORIZATION_DISABLED, 10),
    (CandidateCreateControlFailureCode.AUTHORIZATION_EXPIRED, 10),
    (CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMED, 20),
    (CandidateCreateControlFailureCode.AUTHORIZATION_INVALID, 30),
    (CandidateCreateControlFailureCode.AUTHORIZATION_ACTOR_INVALID, 30),
    (CandidateCreateControlFailureCode.AUTHORIZATION_BINDING_INVALID, 30),
    (CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMPTION_STATE_INVALID, 30),
    (CandidateCreateControlFailureCode.AUTHORIZATION_DURABILITY_FAILED, 30),
]
INPUT_CASES = [(member, 40) for member in CandidateInputFailureCode]
REVIEW_CASES = [
    (ReviewFailureCode.ACTOR_REQUIRED, 40),
    (ReviewFailureCode.ACTOR_INVALID, 40),
    (ReviewFailureCode.ACTOR_UNAUTHORIZED, 40),
    (ReviewFailureCode.SOURCE_IDENTITY_INVALID, 40),
    (ReviewFailureCode.SOURCE_IDENTITY_CONFLICT, 40),
    (ReviewFailureCode.INVALID_REVIEW_REQUEST, 40),
    (ReviewFailureCode.CANDIDATE_OPERATION_FAILED, 50),
    (ReviewFailureCode.INTERNAL_FAILURE, 50),
    (ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS, 50),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("code,expected", CONTROL_CASES)
async def test_all_control_codes(monkeypatch, code, expected) -> None:
    async def reject(_request):
        raise CandidateCreateControlError(code)

    monkeypatch.setattr(harness, "controlled_create_review_candidate", reject)
    raw, digest = transport(valid_value())
    actual, payload = await harness._execute_transport(raw, digest)
    assert actual == decoded(payload)["exit_code"] == expected
    assert decoded(payload)["error_classification"] == code.value


@pytest.mark.asyncio
@pytest.mark.parametrize("code,expected", INPUT_CASES)
async def test_all_candidate_input_codes(monkeypatch, code, expected) -> None:
    async def reject(_request):
        raise CandidateInputError(code)

    monkeypatch.setattr(harness, "controlled_create_review_candidate", reject)
    raw, digest = transport(valid_value())
    actual, payload = await harness._execute_transport(raw, digest)
    assert actual == decoded(payload)["exit_code"] == expected
    assert decoded(payload)["error_classification"] == code.value


@pytest.mark.asyncio
@pytest.mark.parametrize("code,expected", REVIEW_CASES)
async def test_all_review_codes(monkeypatch, code, expected) -> None:
    async def reject(_request):
        raise ReviewApplicationError(code)

    monkeypatch.setattr(harness, "controlled_create_review_candidate", reject)
    raw, digest = transport(valid_value())
    actual, payload = await harness._execute_transport(raw, digest)
    assert actual == decoded(payload)["exit_code"] == expected
    assert decoded(payload)["error_classification"] == code.value


def test_exact_callable_mapping_cardinality_and_no_60_or_70() -> None:
    exits = [expected for _, expected in CONTROL_CASES + INPUT_CASES + REVIEW_CASES]
    assert len(exits) == 24
    assert {number: exits.count(number) for number in (10, 20, 30, 40, 50)} == {
        10: 2,
        20: 1,
        30: 5,
        40: 13,
        50: 3,
    }
    assert exits.count(60) == exits.count(70) == 0


ADVERSARIAL = [
    "X" * 100_000,
    'quotes"and\\backslashes',
    "LF\nCRLF\r\nTAB\t",
    "Unicode-雪-😀-controls-\x00",
    "password=super-secret",
    "postgresql://user:secret@127.0.0.1/db",
    "Bearer abcdef",
    "sk-example-secret",
    "token=secret",
    "PRIVATE KEY",
    '{"authorization_id":"hidden"}',
    "../../etc/passwd",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("untrusted", ADVERSARIAL)
async def test_unknown_exceptions_are_sanitized_and_bounded(monkeypatch, untrusted) -> None:
    marker = f"UNTRUSTED-BEGIN::{untrusted}::UNTRUSTED-END"

    async def reject(_request):
        raise RuntimeError(marker)

    monkeypatch.setattr(harness, "controlled_create_review_candidate", reject)
    raw, digest = transport(valid_value())
    code, payload = await harness._execute_transport(raw, digest)
    value = decoded(payload)
    assert code == value["exit_code"] == 70
    assert value["error_classification"] == "HARNESS_INTERNAL_FAILURE"
    assert marker.encode(errors="ignore") not in payload
    assert b"Traceback" not in payload


@pytest.mark.asyncio
async def test_result_serialization_failure_uses_fixed_exit_60(monkeypatch) -> None:
    async def fake(_request):
        return result()

    def fail_envelope(*_args, **_kwargs):
        raise ValueError("password=must-not-escape")

    monkeypatch.setattr(harness, "controlled_create_review_candidate", fake)
    raw, digest = transport(valid_value())
    monkeypatch.setattr(harness, "_envelope", fail_envelope)
    code, payload = await harness._execute_transport(raw, digest)
    assert code == 60
    value = decoded(payload)
    assert value["exit_classification"] == "HARNESS_OUTPUT_OR_EVIDENCE_DURABILITY_FAILURE"
    assert b"password=" not in payload


class _Sink:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.writes: list[bytes] = []
        self.flushes = 0

    def write(self, payload: bytes) -> int:
        if self.fail:
            raise OSError("secret")
        self.writes.append(payload)
        return len(payload)

    def flush(self) -> None:
        self.flushes += 1


def test_cancelled_error_is_exit_70_and_secret_safe(tmp_path, monkeypatch) -> None:
    calls = 0
    value = valid_value()
    secret_markers = ["password=", "postgresql://", "Bearer", "sk-", "token="]
    value["trusted_receipt_facts"]["supplier_name"] = " ".join(secret_markers)
    raw, digest = transport(value)
    path = tmp_path / "input.json"
    path.write_bytes(raw)
    output = _Sink()
    error = _Sink()

    async def cancel(_request):
        nonlocal calls
        calls += 1
        raise asyncio.CancelledError("password=cancel-secret")

    monkeypatch.setattr(harness, "controlled_create_review_candidate", cancel)
    monkeypatch.setattr(harness.sys, "stdout", SimpleNamespace(buffer=output))
    monkeypatch.setattr(harness.sys, "stderr", SimpleNamespace(buffer=error))
    code = harness.main(
        ["--input-envelope", str(path), "--expected-input-sha256", digest]
    )

    assert code == 70
    assert calls == 1
    assert len(output.writes) == 1
    payload = output.writes[0]
    assert decoded(payload)["error_classification"] == "HARNESS_INTERNAL_FAILURE"
    assert payload.endswith(b"\n") and payload.count(b"\n") == 1
    assert len(payload) <= 4096
    assert error.writes == []
    assert b"Traceback" not in payload
    assert b"CancelledError" not in payload
    assert b"cancel-secret" not in payload
    for marker in secret_markers:
        assert marker.encode() not in payload
    assert harness._state == harness._CLAIMED


def test_main_writes_once_and_governed_stderr_is_empty(tmp_path, monkeypatch) -> None:
    raw, digest = transport(valid_value())
    path = tmp_path / "input.json"
    path.write_bytes(raw)
    output = _Sink()
    error = _Sink()
    monkeypatch.setattr(harness.sys, "stdout", SimpleNamespace(buffer=output))
    monkeypatch.setattr(harness.sys, "stderr", SimpleNamespace(buffer=error))

    async def fake(_raw, _digest):
        return 40, harness._fixed_failure_bytes(40)

    monkeypatch.setattr(harness, "_execute_transport", fake)
    code = harness.main(
        ["--input-envelope", str(path), "--expected-input-sha256", digest]
    )
    assert code == 40
    assert len(output.writes) == 1
    assert len(output.writes[0]) <= 4096
    assert output.flushes == 1
    assert error.writes == []


def test_catastrophic_stdout_failure_has_only_fixed_42_byte_stderr(monkeypatch) -> None:
    output = _Sink(fail=True)
    error = _Sink()
    monkeypatch.setattr(harness.sys, "stdout", SimpleNamespace(buffer=output))
    monkeypatch.setattr(harness.sys, "stderr", SimpleNamespace(buffer=error))
    code = harness.main([])
    assert code == 70
    assert error.writes == [harness.CATASTROPHIC_STDERR]
    assert len(error.writes[0]) == 42
    assert b"Traceback" not in error.writes[0]


def test_static_bypass_and_registration_surfaces_are_absent() -> None:
    source = Path(harness.__file__).read_text()
    for prohibited in (
        "MaterialReceiptRepository",
        "psycopg",
        "execute(",
        "_claim(",
        "authorize_and_consume_candidate_create",
        "CONSUMPTION_DIRECTORY",
        "AUTHORIZATION_PATH",
        "telegram",
        "systemd",
        "cron",
        "scheduler",
        "agent_registry",
        "background_worker",
        "/usr/local/bin",
    ):
        assert prohibited not in source
