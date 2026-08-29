from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import socket
from uuid import uuid4

import pytest

from core.app.input_classifier import InputType
from core.app.material_receipts import candidate_create_authorization as authorization
from core.app.material_receipts import review_use_cases
from core.app.material_receipts.candidate_create_authorization import (
    AUTHORIZATION_SCHEMA_VERSION,
    AuthorizationBoundary,
    CandidateCreateControlError,
    CandidateCreateControlFailureCode as Code,
    authorize_and_consume_candidate_create,
    trusted_facts_sha256,
)
from core.app.material_receipts.candidate_input import (
    TrustedReceiptFacts,
    TrustedReceiptItemFacts,
)
from core.ingestion.universal_ingestion import IngestionResult


NOW = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)
ACTOR = "operator:550e8400-e29b-41d4-a716-446655440000"


def facts() -> TrustedReceiptFacts:
    return TrustedReceiptFacts(
        "PT Stage 033C",
        "DO-033C",
        date(2026, 8, 29),
        NOW,
        (
            TrustedReceiptItemFacts(
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
            ),
        ),
    )


@pytest.fixture
def governed(tmp_path: Path, monkeypatch):
    manifests = tmp_path / "manifests"
    manifests.mkdir(mode=0o700)
    monkeypatch.setattr(review_use_cases, "_MANIFEST_ROOT", manifests)
    identifier = uuid4()
    manifest = manifests / f"{identifier}.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_id": str(identifier),
                "represented_media_type": "text",
                "received_at": "2026-08-29T00:00:00Z",
                "manifest_status": "created",
                "metadata": {"media_type": "text", "character_count": 1},
            }
        ),
        encoding="utf-8",
    )
    evidence = IngestionResult(
        InputType.TEXT,
        InputType.TEXT,
        None,
        str(manifest),
        {},
        "untrusted",
        True,
        False,
        False,
        True,
    )
    consumption = tmp_path / "consumed"
    consumption.mkdir(mode=0o700)
    artifact = tmp_path / "authorization.json"
    boundary = AuthorizationBoundary(
        artifact,
        consumption,
        os.geteuid(),
        os.getegid(),
        os.geteuid(),
        os.getegid(),
    )
    trusted = facts()
    value = {
        "schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "enabled": True,
        "authorization_id": str(uuid4()),
        "not_before_utc": "2026-08-29T11:59:00Z",
        "expires_at_utc": "2026-08-29T12:01:00Z",
        "max_requests": 1,
        "operator_actor_reference": ACTOR,
        "source_manifest_reference": str(manifest),
        "source_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "trusted_facts_sha256": trusted_facts_sha256(trusted),
        "evidence_session_id": "stage033c-test-session",
    }

    def write(current=value) -> None:
        if artifact.exists():
            artifact.chmod(0o600)
        artifact.write_text(
            json.dumps(current, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        artifact.chmod(0o440)

    write()
    return evidence, trusted, boundary, value, write


def claim(governed):
    evidence, trusted, boundary, _, _ = governed
    return authorize_and_consume_candidate_create(
        evidence, trusted, boundary=boundary, clock=lambda: NOW
    )


def asserted(governed, code: Code) -> None:
    with pytest.raises(CandidateCreateControlError) as caught:
        claim(governed)
    assert caught.value.code is code
    assert caught.value.args == (code.value,)


def test_missing_authorization_is_disabled(governed) -> None:
    governed[2].authorization_path.unlink()
    asserted(governed, Code.AUTHORIZATION_DISABLED)


@pytest.mark.parametrize("payload", ["{", "[]", '{"enabled":true,"enabled":true}'])
def test_invalid_or_duplicate_json_fails_closed(governed, payload) -> None:
    governed[2].authorization_path.chmod(0o600)
    governed[2].authorization_path.write_text(payload, encoding="utf-8")
    governed[2].authorization_path.chmod(0o440)
    asserted(governed, Code.AUTHORIZATION_INVALID)


def test_oversized_and_wrong_mode_authorization_fail_closed(governed) -> None:
    path = governed[2].authorization_path
    path.chmod(0o600)
    path.write_bytes(b"x" * (authorization.MAX_AUTHORIZATION_BYTES + 1))
    path.chmod(0o440)
    asserted(governed, Code.AUTHORIZATION_INVALID)
    governed[4]()
    path.chmod(0o640)
    asserted(governed, Code.AUTHORIZATION_INVALID)


def test_symlink_authorization_fails_closed(governed) -> None:
    path = governed[2].authorization_path
    target = path.with_suffix(".target")
    path.rename(target)
    path.symlink_to(target)
    asserted(governed, Code.AUTHORIZATION_INVALID)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("authorization_id", "550E8400-E29B-41D4-A716-446655440000", Code.AUTHORIZATION_INVALID),
        ("authorization_id", "../../marker", Code.AUTHORIZATION_INVALID),
        ("enabled", False, Code.AUTHORIZATION_DISABLED),
        ("max_requests", 2, Code.AUTHORIZATION_DISABLED),
        ("expires_at_utc", "2026-08-29T12:00:00Z", Code.AUTHORIZATION_EXPIRED),
        ("operator_actor_reference", "reviewer:test", Code.AUTHORIZATION_ACTOR_INVALID),
        ("source_manifest_sha256", "0" * 64, Code.AUTHORIZATION_BINDING_INVALID),
        ("trusted_facts_sha256", "0" * 64, Code.AUTHORIZATION_BINDING_INVALID),
        ("source_manifest_reference", "/tmp/unapproved", Code.AUTHORIZATION_INVALID),
    ],
)
def test_invalid_eligibility_rejected_before_claim(governed, field, value, code) -> None:
    governed[3][field] = value
    governed[4]()
    asserted(governed, code)
    assert list(governed[2].consumption_directory.iterdir()) == []


def test_exact_winner_record_and_durability(governed, monkeypatch) -> None:
    calls: list[int] = []
    real_fsync = os.fsync
    monkeypatch.setattr(os, "fsync", lambda fd: (calls.append(fd), real_fsync(fd))[1])
    result = claim(governed)
    assert result.operator_actor_reference == ACTOR
    assert result.consumption_path.name == f"{result.authorization_id}.json"
    assert len(calls) == 2
    assert result.consumption_path.stat().st_mode & 0o777 == 0o600
    record = json.loads(result.consumption_path.read_text(encoding="utf-8"))
    assert set(record) == {
        "schema_version", "authorization_id", "authorization_artifact_sha256",
        "consumed_at_utc", "operator_reference", "source_evidence_sha256",
        "correlation_id", "state",
    }
    assert record["state"] == "CONSUMED"
    assert "password" not in result.consumption_path.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("payload", [b"", b'{"state":'])
def test_existing_empty_or_partial_safe_marker_is_consumed_without_read(
    governed, payload, monkeypatch
) -> None:
    marker = governed[2].consumption_directory / f"{governed[3]['authorization_id']}.json"
    marker.write_bytes(payload)
    marker.chmod(0o600)
    real_open = os.open

    def guarded_open(path, flags, *args):
        if Path(path) == marker and flags & os.O_RDONLY:
            raise AssertionError("loser read marker")
        return real_open(path, flags, *args)

    monkeypatch.setattr(os, "open", guarded_open)
    asserted(governed, Code.AUTHORIZATION_CONSUMED)


@pytest.mark.parametrize("kind", ["symlink", "directory", "fifo", "socket", "wrong_mode"])
def test_unsafe_consumed_object_is_invalid(governed, kind) -> None:
    marker = governed[2].consumption_directory / f"{governed[3]['authorization_id']}.json"
    sock = None
    if kind == "symlink":
        marker.symlink_to(governed[2].authorization_path)
    elif kind == "directory":
        marker.mkdir()
    elif kind == "fifo":
        os.mkfifo(marker)
    elif kind == "socket":
        sock = socket.socket(socket.AF_UNIX)
        short_socket = governed[2].authorization_path.parent / "s"
        sock.bind(str(short_socket))
        short_socket.rename(marker)
    else:
        marker.write_bytes(b"")
        marker.chmod(0o640)
    try:
        asserted(governed, Code.AUTHORIZATION_CONSUMPTION_STATE_INVALID)
    finally:
        if sock is not None:
            sock.close()


def test_arbitrary_n_callers_have_one_winner_and_metadata_only_losers(governed) -> None:
    def attempt(_):
        try:
            claim(governed)
            return "winner"
        except CandidateCreateControlError as exc:
            return exc.code.value

    with ThreadPoolExecutor(max_workers=12) as pool:
        outcomes = list(pool.map(attempt, range(25)))
    assert outcomes.count("winner") == 1
    assert outcomes.count(Code.AUTHORIZATION_CONSUMED.value) == 24


@pytest.mark.parametrize("failed_call", [1, 2])
def test_fsync_failure_keeps_consumed_marker_and_blocks_reuse(
    governed, monkeypatch, failed_call
) -> None:
    calls = 0
    real_fsync = os.fsync

    def fail(fd):
        nonlocal calls
        calls += 1
        if calls == failed_call:
            raise OSError("durability")
        return real_fsync(fd)

    monkeypatch.setattr(os, "fsync", fail)
    asserted(governed, Code.AUTHORIZATION_DURABILITY_FAILED)
    marker = governed[2].consumption_directory / f"{governed[3]['authorization_id']}.json"
    assert marker.exists()
    monkeypatch.setattr(os, "fsync", real_fsync)
    asserted(governed, Code.AUTHORIZATION_CONSUMED)


def test_crash_after_exclusive_creation_remains_consumed_after_restart(governed) -> None:
    marker = governed[2].consumption_directory / f"{governed[3]['authorization_id']}.json"
    fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    asserted(governed, Code.AUTHORIZATION_CONSUMED)
    asserted(governed, Code.AUTHORIZATION_CONSUMED)
    assert marker.exists()
