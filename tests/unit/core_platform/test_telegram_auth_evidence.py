import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from telegram import Update

from core.adapters.telegram import auth_evidence as auth
from core.adapters.telegram import main as adapter


TEXT = "AIOS-PO-AUTH-PR305-" + "a" * 43
SENT = datetime(2026, 9, 28, 1, 0, 10, tzinfo=timezone.utc)
RECEIVED = SENT.replace(microsecond=123456)
BINDING = auth.ChallengeBinding(
    text=TEXT, pr_number=305, head="c5f3bf0e9787998e3c57c429d19a151d9ed5934a",
    approval_record_id="1d3466b9-4d25-492e-9317-22fba2e2dbe7",
    expected_sender_id=961959058, expected_username="bagusder21",
    created_at_utc="2026-09-28T01:00:00.000000Z",
    expires_at_utc="2026-09-28T01:30:00.000000Z",
)


def update(**changes):
    message = {
        "message_id": 51,
        "from": {"id": 961959058, "username": "bagusder21", "is_bot": False,
                 "first_name": "DO NOT RETAIN", "last_name": "PRIVATE"},
        "date": int(SENT.timestamp()),
        "chat": {"id": 961959058, "type": "private", "first_name": "PRIVATE"},
        "text": TEXT,
    }
    message.update(changes)
    return Update.de_json({"update_id": 901, "message": message,
                           "token": "SECRET-TOKEN", "authorization": "SECRET-HEADER"}, None)


def capture(tmp_path, **changes):
    return auth.retain_update(update(**changes), root=tmp_path, received_at=RECEIVED)


def verify(path, root, binding=BINDING):
    return auth.verify_and_consume(path, binding, root=root, verified_at=RECEIVED)


def test_valid_capture_canonical_hash_and_consumption(tmp_path):
    path = capture(tmp_path)
    expected = {
        "schema_version": auth.SCHEMA, "update_id": 901,
        "local_received_at_utc": "2026-09-28T01:00:10.123456Z",
        "message": {"message_id": 51, "from": {"id": 961959058, "username": "bagusder21"},
                    "date": "2026-09-28T01:00:10.000000Z",
                    "chat": {"id": 961959058, "type": "private"}, "text": TEXT},
    }
    raw = path.read_bytes()
    assert raw == (json.dumps(expected, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False) + "\n").encode()
    assert not raw.endswith(b"\n\n")
    assert path.name.split(".")[1] == hashlib.sha256(raw).hexdigest()
    assert path.stat().st_mode & 0o777 == 0o600
    assert not (tmp_path / "consumed").exists()
    assert auth.decode_evidence(raw) == expected
    receipt = json.loads(verify(path, tmp_path).read_bytes())
    assert receipt["telegram_user_id"] == 961959058
    assert receipt["head"] == BINDING.head
    assert receipt["approval_record_id"] == BINDING.approval_record_id
    assert receipt["role_context"]["mode"] == "solo-project-owner-bootstrap"
    assert receipt["evidence_transport_sha256"] == hashlib.sha256(raw).hexdigest()


def test_missing_username_is_nullable_and_numeric_id_is_primary(tmp_path):
    path = capture(tmp_path, **{"from": {"id": 961959058, "is_bot": False, "first_name": "PRIVATE"}})
    receipt = json.loads(verify(path, tmp_path).read_bytes())
    assert receipt["telegram_username"] is None
    assert receipt["telegram_user_id"] == 961959058
    assert receipt["declared_display_username"] == "bagusder21"


@pytest.mark.parametrize("changes", [
    {"from": {"id": 42, "username": "bagusder21", "is_bot": False, "first_name": "X"}},
    {"from": {"id": 961959058, "username": "Bagusder21", "is_bot": False, "first_name": "X"}},
    {"text": "AIOS-PO-AUTH-PR305-" + "b" * 43},
    {"date": int(SENT.replace(hour=2).timestamp())},
    {"date": int(SENT.replace(hour=0).timestamp())},
    {"chat": {"id": -42, "type": "group", "title": "PRIVATE"}},
])
def test_failed_verification_never_consumes(tmp_path, changes):
    path = capture(tmp_path, **changes)
    with pytest.raises(ValueError):
        verify(path, tmp_path)
    assert not (tmp_path / "consumed").exists()


def test_expired_receipt_does_not_consume(tmp_path):
    path = auth.retain_update(update(), root=tmp_path, received_at=RECEIVED.replace(hour=2))
    with pytest.raises(ValueError):
        auth.verify_and_consume(path, BINDING, root=tmp_path, verified_at=RECEIVED.replace(hour=2))
    assert not (tmp_path / "consumed").exists()


@pytest.mark.parametrize("text", ["ordinary private text", TEXT.lower(), TEXT + "\n", " " + TEXT,
                                  "AIOS-PO-AUTH-PR305-short", "status", None])
def test_only_exact_challenge_format_is_captured(tmp_path, text):
    assert capture(tmp_path, text=text) is None
    assert list(tmp_path.iterdir()) == []


def test_no_credential_or_unrelated_private_data_retention(tmp_path):
    raw = capture(tmp_path).read_bytes()
    for forbidden in (b"SECRET", b"PRIVATE", b"DO NOT RETAIN", b"token", b"authorization", b"first_name"):
        assert forbidden not in raw


@pytest.mark.parametrize("field", ["date", "from_user", "chat", "message_id"])
def test_malformed_update_does_not_publish(tmp_path, field):
    message = SimpleNamespace(text=TEXT, date=SENT, from_user=SimpleNamespace(id=1, username=None),
                              chat=SimpleNamespace(id=1, type="private"), message_id=1)
    delattr(message, field)
    with pytest.raises(ValueError):
        auth.retain_update(SimpleNamespace(update_id=1, message=message), root=tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("location", [(), ("message",), ("message", "from"), ("message", "chat")])
def test_unknown_and_duplicate_fields_rejected_at_every_level(tmp_path, location):
    original = json.loads(capture(tmp_path).read_bytes())
    target = original
    for key in location:
        target = target[key]
    target["unknown"] = "SECRET"
    with pytest.raises(ValueError):
        auth.decode_evidence(auth.canonical_bytes(original))
    del target["unknown"]
    # Duplicate a known member in the serialized nested object.
    nested = auth.canonical_bytes(target).rstrip(b"\n")
    key = next(iter(target))
    duplicate = b"{" + json.dumps(key).encode() + b":" + json.dumps(target[key]).encode() + b"," + nested[1:]
    raw = auth.canonical_bytes(original).replace(nested, duplicate, 1)
    with pytest.raises(ValueError, match="duplicate"):
        auth.decode_evidence(raw)


@pytest.mark.parametrize("mutate", [
    lambda b: b + b"\n", lambda b: b.rstrip(b"\n"), lambda b: b.replace(b"\n", b"\r\n"),
    lambda b: b"\xef\xbb\xbf" + b, lambda b: b.replace(b'"update_id":901', b'"update_id":true'),
    lambda b: b.replace(b'"update_id":901', b'"update_id":NaN'),
])
def test_noncanonical_or_invalid_types_rejected(tmp_path, mutate):
    with pytest.raises((ValueError, UnicodeError)):
        auth.decode_evidence(mutate(capture(tmp_path).read_bytes()))


def test_transport_tampering_rejected(tmp_path):
    path = capture(tmp_path)
    path.write_bytes(path.read_bytes().replace(b'"update_id":901', b'"update_id":902'))
    with pytest.raises(ValueError, match="digest"):
        verify(path, tmp_path)
    assert not (tmp_path / "consumed").exists()


def test_replay_and_concurrent_consumption_have_one_winner(tmp_path):
    paths = [capture(tmp_path), capture(tmp_path)]
    assert paths[0] != paths[1]
    assert paths[0].read_bytes() == paths[1].read_bytes()

    def attempt(path):
        try:
            return verify(path, tmp_path)
        except FileExistsError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, paths))
    assert sum(result is not None for result in results) == 1
    before = next((tmp_path / "consumed").iterdir()).read_bytes()
    with pytest.raises(FileExistsError):
        verify(paths[0], tmp_path)
    assert next((tmp_path / "consumed").iterdir()).read_bytes() == before


def test_evidence_filename_collision_never_overwrites(tmp_path, monkeypatch):
    monkeypatch.setattr(auth, "uuid4", lambda: "00000000-0000-4000-8000-000000000001")
    path = capture(tmp_path)
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        capture(tmp_path)
    assert path.read_bytes() == before


def test_failed_fsync_does_not_publish(tmp_path, monkeypatch):
    def fail(fd):
        raise OSError("disk failure")
    monkeypatch.setattr(auth.os, "fsync", fail)
    with pytest.raises(OSError):
        capture(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_old_incomplete_manifest_cannot_be_promoted(tmp_path):
    path = tmp_path / "old.json"
    path.write_text('{"telegram_user_id":961959058,"metadata":{"character_count":62}}')
    before = path.read_bytes()
    with pytest.raises(ValueError):
        verify(path, tmp_path)
    assert path.read_bytes() == before
    assert not (tmp_path / "consumed").exists()


@pytest.mark.parametrize("binding", [replace(BINDING, pr_number=304), replace(BINDING, head="bad"),
                                     replace(BINDING, approval_record_id="bad")])
def test_invalid_subject_binding_never_consumes(tmp_path, binding):
    with pytest.raises(ValueError):
        verify(capture(tmp_path), tmp_path, binding)
    assert not (tmp_path / "consumed").exists()


def test_unicode_is_literal_utf8(tmp_path):
    path = capture(tmp_path, **{"from": {"id": 961959058, "is_bot": False, "first_name": "X", "username": "é"}})
    assert "é".encode() in path.read_bytes()
    assert b"\\u00e9" not in path.read_bytes()


@pytest.mark.parametrize("capture_fails", [False, True])
def test_receiver_captures_before_ingestion_and_preserves_message(tmp_path, monkeypatch, caplog, capture_fails):
    import asyncio
    original = update()
    events = []

    def retain(value):
        assert value is original
        events.append("capture")
        if capture_fails:
            raise OSError("SECRET must not enter logs")
        return auth.retain_update(value, root=tmp_path, received_at=RECEIVED)

    async def ingest(message, context):
        events.append("ingest")
        assert message is original.message
        assert message.text == TEXT
        return SimpleNamespace(register_handoff_ready=False)

    monkeypatch.setattr(adapter, "retain_update", retain)
    monkeypatch.setattr(adapter, "ingest_telegram_message", AsyncMock(side_effect=ingest))
    asyncio.run(adapter.handle_update(original, SimpleNamespace()))
    assert events == ["capture", "ingest"]
    assert not (tmp_path / "consumed").exists()
    assert "SECRET" not in caplog.text
    assert TEXT not in caplog.text


def test_new_nested_archive_and_consumption_are_durable(tmp_path, monkeypatch):
    root = tmp_path / "authentication-evidence" / "telegram"
    actual = auth.os.fsync
    calls = []

    def sync(fd):
        calls.append(fd)
        actual(fd)

    monkeypatch.setattr(auth.os, "fsync", sync)
    path = capture(root)
    verify(path, root)
    # Parent fsyncs for three new directories, plus file/directory for two records.
    assert len(calls) == 7
    assert root.stat().st_mode & 0o777 == 0o700


def test_symlink_evidence_and_archive_are_rejected(tmp_path):
    root = tmp_path / "real"
    path = capture(root)
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError):
        capture(alias)
    with pytest.raises(ValueError):
        verify(alias / path.name, alias)
    linked = root / "link.json"
    linked.symlink_to(path)
    with pytest.raises(OSError):
        verify(linked, root)
    assert not (root / "consumed").exists()
