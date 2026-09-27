import asyncio
import hashlib
import os
import stat
from threading import Event
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
    assert not list((tmp_path / "consumed").glob("*.json"))
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
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_expired_receipt_does_not_consume(tmp_path):
    path = auth.retain_update(update(), root=tmp_path, received_at=RECEIVED.replace(hour=2))
    with pytest.raises(ValueError):
        auth.verify_and_consume(path, BINDING, root=tmp_path, verified_at=RECEIVED.replace(hour=2))
    assert not list((tmp_path / "consumed").glob("*.json"))


@pytest.mark.parametrize("text", ["ordinary private text", TEXT.lower(), TEXT + "\n", " " + TEXT,
                                  "AIOS-PO-AUTH-PR305-short", "status", None])
def test_only_exact_challenge_format_is_captured(tmp_path, text):
    assert capture(tmp_path, text=text) is None
    assert not list(tmp_path.glob("*.json"))


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
    assert not list(tmp_path.glob("*.json"))


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
    with pytest.raises(ValueError, match="completion|digest"):
        verify(path, tmp_path)
    assert not list((tmp_path / "consumed").glob("*.json"))


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
    before = next((tmp_path / "consumed").glob("*.json")).read_bytes()
    with pytest.raises(FileExistsError):
        verify(paths[0], tmp_path)
    assert next((tmp_path / "consumed").glob("*.json")).read_bytes() == before


def test_evidence_filename_collision_never_overwrites(tmp_path, monkeypatch):
    path = capture(tmp_path)
    before = path.read_bytes()
    actual = auth.uuid4
    calls = 0

    def collision():
        nonlocal calls
        calls += 1
        return path.name.split(".")[0] if calls == 1 else actual()

    monkeypatch.setattr(auth, "uuid4", collision)
    with pytest.raises(auth.PublicationError) as error:
        capture(tmp_path)
    assert error.value.state == auth.PublicationState.NOT_PUBLISHED
    assert path.read_bytes() == before


def test_failed_fsync_does_not_publish(tmp_path, monkeypatch):
    def fail(fd):
        raise OSError("disk failure")
    monkeypatch.setattr(auth.os, "fsync", fail)
    with pytest.raises(OSError):
        capture(tmp_path)
    assert not list(tmp_path.glob("*.json"))


def test_old_incomplete_manifest_cannot_be_promoted(tmp_path):
    path = tmp_path / "old.json"
    path.write_text('{"telegram_user_id":961959058,"metadata":{"character_count":62}}')
    before = path.read_bytes()
    with pytest.raises((ValueError, OSError)):
        verify(path, tmp_path)
    assert path.read_bytes() == before
    assert not list((tmp_path / "consumed").glob("*.json"))


@pytest.mark.parametrize("binding", [replace(BINDING, pr_number=304), replace(BINDING, head="bad"),
                                     replace(BINDING, approval_record_id="bad")])
def test_invalid_subject_binding_never_consumes(tmp_path, binding):
    with pytest.raises(ValueError):
        verify(capture(tmp_path), tmp_path, binding)
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_unicode_is_literal_utf8(tmp_path):
    path = capture(tmp_path, **{"from": {"id": 961959058, "is_bot": False, "first_name": "X", "username": "é"}})
    assert "é".encode() in path.read_bytes()
    assert b"\\u00e9" not in path.read_bytes()


@pytest.mark.parametrize("capture_fails", [False, True])
def test_receiver_captures_before_ingestion_and_preserves_message(tmp_path, monkeypatch, caplog, capture_fails):
    original = update()
    events = []
    dispatcher = auth.CaptureDispatcher(tmp_path)
    project = auth._project_update
    store = auth._store

    def snapshot(value, received_at=None):
        assert value is original
        events.append("snapshot")
        return project(value, received_at=RECEIVED)

    def retain(data, root):
        if capture_fails:
            raise auth.PublicationError(auth.PublicationState.NOT_PUBLISHED)
        return store(data, root)

    async def ingest(message, context):
        events.append("ingest")
        assert message is original.message
        assert message.text == TEXT
        return SimpleNamespace(register_handoff_ready=False)

    monkeypatch.setattr(auth, "_project_update", snapshot)
    monkeypatch.setattr(auth, "_store", retain)
    monkeypatch.setattr(adapter, "CAPTURE_DISPATCHER", dispatcher)
    monkeypatch.setattr(adapter, "ingest_telegram_message", AsyncMock(side_effect=ingest))
    try:
        asyncio.run(adapter.handle_update(original, SimpleNamespace()))
    finally:
        dispatcher.close()
    assert events == ["snapshot", "ingest"]
    assert not list((tmp_path / "consumed").glob("*.json"))
    assert TEXT not in caplog.text


def test_symlink_evidence_and_archive_are_rejected(tmp_path):
    root = tmp_path / "real"
    path = capture(root)
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(auth.PublicationError):
        capture(alias)
    with pytest.raises((ValueError, OSError)):
        verify(alias / path.name, alias)
    linked = root / "link.json"
    linked.symlink_to(path)
    with pytest.raises(OSError):
        verify(linked, root)
    assert not list((root / "consumed").glob("*.json"))


@pytest.mark.parametrize("which", ["parent", "ancestor"])
def test_adversarial_directory_symlink_component(tmp_path, which):
    real = tmp_path / "real"
    real.mkdir(mode=0o700)
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    root = alias / "archive" if which == "parent" else alias / "nested" / "archive"
    with pytest.raises(auth.PublicationError) as error:
        capture(root)
    assert error.value.state == auth.PublicationState.NOT_PUBLISHED
    assert not list(real.rglob("*.json"))


@pytest.mark.parametrize("which", ["ancestor", "archive", "consumed"])
def test_adversarial_directory_swapped_after_validation(tmp_path, monkeypatch, which):
    parent = tmp_path / "parent"
    root = parent / "archive"
    path = capture(root)
    original_link = auth.os.link
    swapped = False
    target = {"ancestor": parent, "archive": root, "consumed": root / "consumed"}[which]
    moved = target.with_name(target.name + "-original")

    def swap_then_link(src, dst, **kwargs):
        nonlocal swapped
        if not swapped and not str(dst).endswith(".complete"):
            swapped = True
            target.rename(moved)
            target.mkdir(mode=0o700)
        return original_link(src, dst, **kwargs)

    monkeypatch.setattr(auth.os, "link", swap_then_link)
    with pytest.raises(auth.PublicationError) as error:
        verify(path, root)
    assert error.value.state == auth.PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
    assert not list(target.rglob("*.json"))
    assert not list(moved.rglob("consumed/*.complete"))
    # A subsequent verifier must reject the changed layout rather than reinitialize it.
    with pytest.raises((ValueError, OSError)):
        verify(path, root)


def test_adversarial_directory_archive_replaced_during_capture(tmp_path, monkeypatch):
    root = tmp_path / "archive"
    capture(root)
    original_link = auth.os.link
    moved = tmp_path / "old-archive"
    swapped = False

    def replace(src, dst, **kwargs):
        nonlocal swapped
        if not swapped and str(dst).endswith(".json"):
            swapped = True
            root.rename(moved)
            root.mkdir(mode=0o700)
        return original_link(src, dst, **kwargs)

    monkeypatch.setattr(auth.os, "link", replace)
    with pytest.raises(auth.PublicationError) as error:
        capture(root)
    assert error.value.state == auth.PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
    assert not list(root.iterdir())
    assert len(list(moved.glob("*.json"))) == 2
    assert len(list(moved.glob("*.complete"))) == 1


def test_adversarial_directory_replay_after_consumed_swap(tmp_path):
    path = capture(tmp_path)
    receipt = verify(path, tmp_path)
    before = receipt.read_bytes()
    consumed = tmp_path / "consumed"
    consumed.rename(tmp_path / "old-consumed")
    consumed.mkdir(mode=0o700)
    with pytest.raises(ValueError, match="identity"):
        verify(path, tmp_path)
    assert not list(consumed.iterdir())
    assert (tmp_path / "old-consumed" / receipt.name).read_bytes() == before
    # A new capture cannot reset the anchored replay namespace either.
    with pytest.raises(auth.PublicationError):
        capture(tmp_path)


def test_adversarial_directory_stable_path_and_descriptor_relative_io(tmp_path, monkeypatch):
    original_link = auth.os.link
    calls = []

    def relative(src, dst, **kwargs):
        assert "/" not in str(src) and "/" not in str(dst)
        assert kwargs["src_dir_fd"] == kwargs["dst_dir_fd"]
        assert kwargs["follow_symlinks"] is False
        calls.append(dst)
        return original_link(src, dst, **kwargs)

    monkeypatch.setattr(auth.os, "link", relative)
    path = capture(tmp_path)
    receipt = verify(path, tmp_path)
    assert receipt.exists()
    assert path.with_name(path.name + ".complete").exists()
    assert len(calls) == 5  # anchor, evidence+completion, consumption+completion


@pytest.mark.parametrize("mode", [0o755, 0o770, 0o777])
def test_adversarial_directory_unsafe_permissions(tmp_path, mode):
    root = tmp_path / "archive"
    root.mkdir(mode=mode)
    root.chmod(mode)
    with pytest.raises(auth.PublicationError):
        capture(root)
    assert not list(root.glob("*.json"))


def test_adversarial_directory_mode_change_after_validation(tmp_path):
    path = capture(tmp_path)
    with auth.PinnedArchive(tmp_path) as archive:
        (tmp_path / "consumed").chmod(0o750)
        with pytest.raises(ValueError, match="identity"):
            archive.validate()
    with pytest.raises((ValueError, OSError)):
        verify(path, tmp_path)


@pytest.mark.parametrize("field", ["st_dev", "st_ino", "st_uid", "st_gid", "st_mode"])
def test_adversarial_directory_revalidates_all_identity_fields(tmp_path, monkeypatch, field):
    capture(tmp_path)
    with auth.PinnedArchive(tmp_path) as archive:
        actual = auth.os.fstat
        def changed(fd):
            value = actual(fd)
            if fd != archive.root_fd:
                return value
            fields = {name: getattr(value, name) for name in
                      ("st_dev", "st_ino", "st_uid", "st_gid", "st_mode")}
            fields[field] += 1
            return SimpleNamespace(**fields)
        monkeypatch.setattr(auth.os, "fstat", changed)
        with pytest.raises(ValueError, match="identity"):
            archive.validate()


def test_adversarial_directory_parent_replaced_cannot_reinitialize_replay_namespace(tmp_path):
    parent = tmp_path / "private-parent"
    root = parent / "archive"
    path = capture(root)
    verify(path, root)
    parent.rename(tmp_path / "previous-parent")
    parent.mkdir(mode=0o700)
    with pytest.raises(auth.PublicationError):
        capture(root)
    assert not list(parent.iterdir())


def test_adversarial_directory_archive_replacement_rejected_after_reopen(tmp_path, monkeypatch):
    root = tmp_path / "archive"
    capture(root)
    root.rename(tmp_path / "old-archive")
    root.mkdir(mode=0o700)
    # Simulate a new process: the persisted parent anchor still pins the archive.
    monkeypatch.setattr(auth, "_KNOWN_LAYOUTS", {})
    with pytest.raises(auth.PublicationError):
        capture(root)
    assert not list(root.glob("*.json"))


def test_adversarial_directory_unsafe_owner_rejected(tmp_path, monkeypatch):
    root = tmp_path / "archive"
    root.mkdir(mode=0o700)
    target = root.stat().st_ino
    actual = auth.os.fstat
    def wrong_owner(fd):
        value = actual(fd)
        if value.st_ino != target:
            return value
        return SimpleNamespace(st_dev=value.st_dev, st_ino=value.st_ino,
                               st_uid=os.geteuid() + 1000, st_gid=value.st_gid,
                               st_mode=value.st_mode)
    monkeypatch.setattr(auth.os, "fstat", wrong_owner)
    with pytest.raises(auth.PublicationError):
        capture(root)
    assert not list(root.iterdir())


def test_adversarial_async_slow_fsync_heartbeat_ordinary_ingestion_and_overload(tmp_path, monkeypatch, caplog):
    started, release = Event(), Event()
    original_fsync = auth.os.fsync
    calls = []
    dispatcher = auth.CaptureDispatcher(tmp_path)

    def stalled(fd):
        started.set()
        assert release.wait(5), "test did not release simulated disk"
        return original_fsync(fd)

    async def ingest(message, context):
        calls.append(message.text)
        return SimpleNamespace(register_handoff_ready=False)

    monkeypatch.setattr(auth.os, "fsync", stalled)
    monkeypatch.setattr(adapter, "CAPTURE_DISPATCHER", dispatcher)
    monkeypatch.setattr(adapter, "ingest_telegram_message", AsyncMock(side_effect=ingest))

    async def exercise():
        await adapter.handle_update(update(), SimpleNamespace())
        for _ in range(100):
            if started.is_set():
                break
            await asyncio.sleep(.005)
        assert started.is_set()
        ticks = []
        async def heartbeat():
            for _ in range(3):
                await asyncio.sleep(.005)
                ticks.append(1)
        await asyncio.wait_for(asyncio.gather(
            heartbeat(), adapter.handle_update(update(text="ordinary business text"), SimpleNamespace())
        ), timeout=1)
        assert len(ticks) == 3 and not release.is_set()
        assert calls == [TEXT, "ordinary business text"]
        # No executor backlog: all additional auth submissions fail immediately.
        assert [dispatcher.submit(update()) for _ in range(20)] == ["REJECTED_CAPACITY"] * 20
        await adapter.handle_update(update(), SimpleNamespace())
        assert calls == [TEXT, "ordinary business text", TEXT]
        assert not list((tmp_path / "consumed").glob("*.json"))

    try:
        asyncio.run(exercise())
    finally:
        release.set()
        dispatcher.close()
    assert "capacity exhausted" in caplog.text
    assert len(list(tmp_path.glob("*.json"))) == 1
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_adversarial_async_concurrent_admission_has_no_waiting_jobs(tmp_path, monkeypatch):
    started, release = Event(), Event()
    actual = auth._store
    calls = []
    dispatcher = auth.CaptureDispatcher(tmp_path)
    def store(data, root):
        calls.append(data)
        started.set()
        assert release.wait(5)
        return actual(data, root)
    monkeypatch.setattr(auth, "_store", store)
    try:
        with ThreadPoolExecutor(max_workers=8) as submitters:
            statuses = list(submitters.map(lambda _: dispatcher.submit(update()), range(24)))
        assert started.wait(1)
        assert statuses.count("ADMITTED") == 1
        assert statuses.count("REJECTED_CAPACITY") == 23
        assert len(calls) == 1
    finally:
        release.set()
        dispatcher.close()
    assert len(list(tmp_path.glob("*.json"))) == 1
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_adversarial_async_worker_start_failure_closes_admission(tmp_path, monkeypatch, caplog):
    dispatcher = auth.CaptureDispatcher(tmp_path)
    def unavailable():
        raise RuntimeError("injected worker start failure")
    monkeypatch.setattr(dispatcher.executor, "_adjust_thread_count", unavailable)
    monkeypatch.setattr(adapter, "CAPTURE_DISPATCHER", dispatcher)
    ingestion = AsyncMock(return_value=SimpleNamespace(register_handoff_ready=False))
    monkeypatch.setattr(adapter, "ingest_telegram_message", ingestion)
    try:
        assert dispatcher.submit(update()) == "NOT_PUBLISHED"
        assert dispatcher.executor._shutdown
        assert dispatcher.submit(update()) == "NOT_PUBLISHED"
        asyncio.run(adapter.handle_update(update(text="ordinary"), SimpleNamespace()))
        ingestion.assert_awaited_once()
    finally:
        dispatcher.close()
    assert not list(tmp_path.glob("*.json"))
    assert "worker unavailable" in caplog.text


@pytest.mark.parametrize("failure", ["file_fsync", "before_link", "after_link", "parent_fsync", "readback", "completion_link"])
def test_adversarial_durability_publication_failure_states(tmp_path, monkeypatch, failure):
    # Initialize the layout without retaining any platform evidence.
    with auth.PinnedArchive(tmp_path, create=True):
        pass
    fsync, link, read = auth.os.fsync, auth.os.link, auth.PinnedArchive.read
    published = False

    def failing_fsync(fd):
        is_dir = stat.S_ISDIR(os.fstat(fd).st_mode)
        if (failure == "file_fsync" and not is_dir) or (failure == "parent_fsync" and is_dir and published):
            raise OSError("injected fsync failure")
        return fsync(fd)

    def failing_link(src, dst, **kwargs):
        nonlocal published
        if failure == "before_link" or (failure == "completion_link" and str(dst).endswith(".complete")):
            raise OSError("injected link failure")
        result = link(src, dst, **kwargs)
        if str(dst).endswith(".json"):
            published = True
            if failure == "after_link":
                raise OSError("injected failure after payload publication")
        return result

    def failing_read(self, fd, name):
        if failure == "readback" and not name.startswith("."):
            raise ValueError("injected readback verification failure")
        return read(self, fd, name)

    with monkeypatch.context() as m:
        m.setattr(auth.os, "fsync", failing_fsync)
        m.setattr(auth.os, "link", failing_link)
        m.setattr(auth.PinnedArchive, "read", failing_read)
        with pytest.raises(auth.PublicationError) as error:
            capture(tmp_path)
    records = list(tmp_path.glob("*.json"))
    before_publication = failure in ("file_fsync", "before_link")
    assert error.value.state == (auth.PublicationState.NOT_PUBLISHED if before_publication
                                 else auth.PublicationState.PUBLISHED_DURABILITY_UNCERTAIN)
    assert len(records) == (0 if before_publication else 1)
    assert not list(tmp_path.glob("*.complete"))
    for path in records:
        before = path.read_bytes()
        with pytest.raises((ValueError, OSError)):
            verify(path, tmp_path)
        assert path.read_bytes() == before
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_adversarial_durability_parent_creation_fsync_failure(tmp_path, monkeypatch):
    root = tmp_path / "archive"
    def fail(fd):
        raise OSError("injected parent fsync failure")
    monkeypatch.setattr(auth.os, "fsync", fail)
    with pytest.raises(auth.PublicationError) as error:
        capture(root)
    assert error.value.state == auth.PublicationState.NOT_PUBLISHED
    assert not list(root.glob("*.json"))


def test_adversarial_durability_success_requires_final_attempt_commit(tmp_path, monkeypatch):
    events = []
    fsync, link = auth.os.fsync, auth.os.link
    def synced(fd):
        events.append("fsync")
        return fsync(fd)
    def linked(src, dst, **kwargs):
        events.append("complete" if str(dst).endswith(".complete") else "link")
        return link(src, dst, **kwargs)
    monkeypatch.setattr(auth.os, "fsync", synced)
    monkeypatch.setattr(auth.os, "link", linked)
    path = capture(tmp_path)
    assert events.index("complete") < len(events) - 1
    assert events[-1] == "fsync"
    assert attempt_states(path) == ["PENDING", "COMMITTED"]
    assert json.loads(path.with_name(path.name + ".complete").read_bytes())["state"] == "DURABLY_PUBLISHED"
    assert verify(path, tmp_path).exists()


def test_adversarial_durability_missing_or_changed_completion_rejects(tmp_path):
    path = capture(tmp_path)
    completion = path.with_name(path.name + ".complete")
    completion.write_bytes(b"{}\n")
    with pytest.raises(ValueError, match="completion"):
        verify(path, tmp_path)
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_adversarial_durability_orphan_certificate_cannot_authorize_new_publication(tmp_path, monkeypatch):
    path = capture(tmp_path)
    # Preserve the previous payload for inspection, leaving its certificate orphaned.
    path.rename(tmp_path / "retained-previous-payload")
    actual = auth.uuid4
    calls = 0
    def collision():
        nonlocal calls
        calls += 1
        return path.name.split(".")[0] if calls == 1 else actual()
    monkeypatch.setattr(auth, "uuid4", collision)
    with pytest.raises(auth.PublicationError) as error:
        capture(tmp_path)
    assert error.value.state == auth.PublicationState.NOT_PUBLISHED
    assert not path.exists()
    with pytest.raises(OSError):
        verify(path, tmp_path)
    assert not list((tmp_path / "consumed").glob("*.json"))


def attempt_states(path):
    return [json.loads(line)["state"] for line in
            path.with_name(path.name + ".attempt").read_bytes().splitlines()]


@pytest.mark.parametrize("point", ["completion_link", "post_link_validation", "completion_fsync",
                                   "staging_cleanup", "committed_state", "guard_retirement"])
def test_completion_outcome_error_after_effect_is_permanently_ineligible(tmp_path, monkeypatch, point):
    root = tmp_path / "archive"
    with auth.PinnedArchive(root, create=True):
        pass
    link, fsync, unlink = auth.os.link, auth.os.fsync, auth.os.unlink
    check, append = auth.PinnedArchive.current_objects, auth._append_attempt
    fired = False

    def completion_exists():
        return bool(list(root.glob("*.complete")))

    def linked(src, dst, **kwargs):
        nonlocal fired
        result = link(src, dst, **kwargs)
        if point == "completion_link" and str(dst).endswith(".complete") and not fired:
            fired = True
            raise OSError("injected after completion link succeeded")
        return result

    def checked(self, fd, objects):
        nonlocal fired
        if point == "post_link_validation" and completion_exists() and not fired:
            fired = True
            raise OSError("injected before final namespace check")
        return check(self, fd, objects)

    def synced(fd):
        nonlocal fired
        result = fsync(fd)
        if (point == "completion_fsync" and stat.S_ISDIR(os.fstat(fd).st_mode)
                and completion_exists() and not fired):
            fired = True
            raise OSError("injected after completion directory fsync")
        return result

    def appended(fd, name, data, state):
        nonlocal fired
        result = append(fd, name, data, state)
        if point == "committed_state" and state == "COMMITTED" and not fired:
            fired = True
            raise OSError("injected after provisional committed journal fsync")
        return result

    def unlinked(name, **kwargs):
        nonlocal fired
        if (point == "staging_cleanup" and str(name).endswith(".tmp")
                and completion_exists() and not fired):
            fired = True
            raise OSError("injected required staging cleanup failure")
        result = unlink(name, **kwargs)
        if point == "guard_retirement" and str(name).endswith(".pending") and not fired:
            fired = True
            raise OSError("injected after pending guard unlink")
        return result

    with monkeypatch.context() as m:
        m.setattr(auth.os, "link", linked)
        m.setattr(auth.os, "fsync", synced)
        m.setattr(auth.os, "unlink", unlinked)
        m.setattr(auth.PinnedArchive, "current_objects", checked)
        m.setattr(auth, "_append_attempt", appended)
        with pytest.raises(auth.PublicationError) as error:
            capture(root)
    assert fired
    assert error.value.state == auth.PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
    path = next(root.glob("*.json"))
    assert path.with_name(path.name + ".complete").exists()
    assert path.with_name(path.name + ".pending").exists()
    assert attempt_states(path)[-1] == "UNCERTAIN"
    before = path.read_bytes()
    # Also prove denial without any process-local uncertain-attempt cache.
    monkeypatch.setattr(auth, "_UNCERTAIN_ATTEMPTS", set())
    with pytest.raises(ValueError):
        verify(path, root)
    assert path.read_bytes() == before
    assert not list((root / "consumed").glob("*.json"))


@pytest.mark.parametrize("extra_states", [["UNCERTAIN"], ["UNCERTAIN", "COMMITTED"]])
def test_completion_outcome_certificate_cannot_override_uncertain_state(tmp_path, extra_states):
    path = capture(tmp_path)
    with path.with_name(path.name + ".attempt").open("ab") as stream:
        for state in extra_states:
            stream.write(auth._attempt_record(path.name, path.read_bytes(), state))
    with pytest.raises(ValueError, match="attempt"):
        verify(path, tmp_path)
    assert path.with_name(path.name + ".complete").exists()
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_completion_outcome_guard_denies_when_uncertain_journal_append_fails(tmp_path, monkeypatch):
    link, append = auth.os.link, auth._append_attempt
    def failed_link(src, dst, **kwargs):
        result = link(src, dst, **kwargs)
        if str(dst).endswith(".complete"):
            raise OSError("after-effect completion failure")
        return result
    def failed_append(fd, name, data, state):
        if state == "UNCERTAIN":
            raise OSError("journal unavailable")
        return append(fd, name, data, state)
    with monkeypatch.context() as m:
        m.setattr(auth.os, "link", failed_link)
        m.setattr(auth, "_append_attempt", failed_append)
        with pytest.raises(auth.PublicationError):
            capture(tmp_path)
    path = next(tmp_path.glob("*.json"))
    monkeypatch.setattr(auth, "_UNCERTAIN_ATTEMPTS", set())
    assert attempt_states(path) == ["PENDING"]
    with pytest.raises(ValueError):
        verify(path, tmp_path)
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_completion_outcome_reader_cannot_observe_provisional_commit(tmp_path, monkeypatch):
    reached, release = Event(), Event()
    append = auth._append_attempt
    def pause_then_fail(fd, name, data, state):
        result = append(fd, name, data, state)
        if state == "COMMITTED":
            reached.set()
            assert release.wait(5)
            raise OSError("final validation not complete")
        return result
    monkeypatch.setattr(auth, "_append_attempt", pause_then_fail)
    with ThreadPoolExecutor(max_workers=2) as pool:
        writer = pool.submit(capture, tmp_path)
        reader = None
        try:
            assert reached.wait(3)
            path = next(tmp_path.glob("*.json"))
            reader = pool.submit(verify, path, tmp_path)
            with pytest.raises(TimeoutError):
                reader.result(timeout=.05)
        finally:
            release.set()
        with pytest.raises(auth.PublicationError):
            writer.result(timeout=3)
        with pytest.raises(ValueError):
            reader.result(timeout=3)
    assert not list((tmp_path / "consumed").glob("*.json"))


@pytest.mark.parametrize("which", ["archive", "consumed"])
@pytest.mark.parametrize("when", ["before_link", "after_link", "after_state"])
def test_final_namespace_swap_never_reports_success(tmp_path, monkeypatch, which, when):
    root = tmp_path / "archive"
    path = capture(root)
    link, append = auth.os.link, auth._append_attempt
    target = root if which == "archive" else root / "consumed"
    moved = tmp_path / ("old-" + which)
    swapped = False
    def swap():
        nonlocal swapped
        target.rename(moved)
        target.mkdir(mode=0o700)
        swapped = True
    def linked(src, dst, **kwargs):
        if str(dst).endswith(".complete") and when == "before_link" and not swapped:
            swap()
        result = link(src, dst, **kwargs)
        if str(dst).endswith(".complete") and when == "after_link" and not swapped:
            swap()
        return result
    def appended(fd, name, data, state):
        result = append(fd, name, data, state)
        if state == "COMMITTED" and when == "after_state" and not swapped:
            swap()
        return result
    with monkeypatch.context() as m:
        m.setattr(auth.os, "link", linked)
        m.setattr(auth, "_append_attempt", appended)
        with pytest.raises(auth.PublicationError) as error:
            verify(path, root)
    assert swapped
    assert error.value.state == auth.PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
    assert not list(target.iterdir())
    old_consumed = moved / "consumed" if which == "archive" else moved
    receipt = next(old_consumed.glob("*.json"))
    assert receipt.with_name(receipt.name + ".complete").exists()
    assert attempt_states(receipt)[-1] == "UNCERTAIN"
    # Restore the original namespace: the terminal journal still prevents replay.
    target.rmdir()
    moved.rename(target)
    with pytest.raises(FileExistsError):
        verify(path, root)


def test_final_namespace_missing_returned_payload_rejects_commit(tmp_path, monkeypatch):
    append = auth._append_attempt
    moved = tmp_path / "retained-renamed-payload"
    def move_after_state(fd, name, data, state):
        result = append(fd, name, data, state)
        if state == "COMMITTED":
            (tmp_path / name).rename(moved)
        return result
    monkeypatch.setattr(auth, "_append_attempt", move_after_state)
    with pytest.raises(auth.PublicationError) as error:
        capture(tmp_path)
    assert error.value.state == auth.PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
    assert moved.exists()
    attempt = next(tmp_path.glob("*.attempt"))
    assert json.loads(attempt.read_bytes().splitlines()[-1])["state"] == "UNCERTAIN"
    assert not list((tmp_path / "consumed").glob("*.json"))


def test_final_namespace_stable_names_reference_committed_objects(tmp_path):
    path = capture(tmp_path)
    receipt = verify(path, tmp_path)
    for record in (path, receipt):
        assert record.exists()
        assert record.with_name(record.name + ".complete").exists()
        assert not record.with_name(record.name + ".pending").exists()
        assert attempt_states(record) == ["PENDING", "COMMITTED"]


@pytest.mark.parametrize("target", ["/", "archive", "consumed", "attempt", "evidence", "certificate"])
def test_descriptor_ownership_first_fstat_failure_returns_to_baseline(tmp_path, monkeypatch, target):
    root = tmp_path / "archive"
    path = capture(root)
    opened, actual_stat = auth.os.open, auth.os.fstat
    descriptors = {}
    fired = False
    def tracked_open(name, *args, **kwargs):
        fd = opened(name, *args, **kwargs)
        descriptors[fd] = str(name)
        return fd
    def fail_first(fd):
        nonlocal fired
        name = descriptors.get(fd)
        selected = (name == target or target == "attempt" and name == path.name + ".attempt"
                    or target == "evidence" and name == path.name
                    or target == "certificate" and name == path.name + ".complete")
        if selected and not fired:
            fired = True
            raise OSError("injected first metadata failure")
        return actual_stat(fd)
    baseline = len(os.listdir("/proc/self/fd"))
    with monkeypatch.context() as m:
        m.setattr(auth.os, "open", tracked_open)
        m.setattr(auth.os, "fstat", fail_first)
        with pytest.raises(OSError):
            verify(path, root)
    assert fired
    assert len(os.listdir("/proc/self/fd")) == baseline
    assert not list((root / "consumed").glob("*.json"))


def test_descriptor_ownership_new_attempt_metadata_failure_closes_fd(tmp_path, monkeypatch):
    opened, actual_stat = auth.os.open, auth.os.fstat
    descriptors = {}
    fired = False
    def tracked_open(name, *args, **kwargs):
        fd = opened(name, *args, **kwargs)
        descriptors[fd] = str(name)
        return fd
    def fail_first(fd):
        nonlocal fired
        if descriptors.get(fd, "").endswith(".attempt") and not fired:
            fired = True
            raise OSError("injected new attempt fstat failure")
        return actual_stat(fd)
    baseline = len(os.listdir("/proc/self/fd"))
    with monkeypatch.context() as m:
        m.setattr(auth.os, "open", tracked_open)
        m.setattr(auth.os, "fstat", fail_first)
        with pytest.raises(auth.PublicationError):
            capture(tmp_path)
    assert fired
    assert len(os.listdir("/proc/self/fd")) == baseline
    assert not list(tmp_path.glob("*.json"))


@pytest.mark.parametrize("operation", ["stage", "pending_guard", "evidence_read", "attempt_read"])
def test_descriptor_ownership_stream_wrapper_failure_closes_fd(tmp_path, monkeypatch, operation):
    path = capture(tmp_path)
    data = path.read_bytes()
    with auth.PinnedArchive(tmp_path) as archive:
        baseline = len(os.listdir("/proc/self/fd"))
        def fail_wrapper(*args, **kwargs):
            raise OSError("injected stream wrapper failure")
        with monkeypatch.context() as m:
            m.setattr(auth.os, "fdopen", fail_wrapper)
            with pytest.raises(OSError):
                if operation == "stage":
                    archive.stage(archive.root_fd, data)
                elif operation == "pending_guard":
                    auth._pending_guard(archive.root_fd, "probe", data)
                elif operation == "evidence_read":
                    archive.read(archive.root_fd, path.name)
                else:
                    with auth._committed_attempt(archive, archive.root_fd, path.name, data):
                        pytest.fail("stream failure was not propagated")
        assert len(os.listdir("/proc/self/fd")) == baseline
