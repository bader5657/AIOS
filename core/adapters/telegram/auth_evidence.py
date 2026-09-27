"""Bounded Telegram challenge capture; capture alone never authenticates an Owner."""

import hashlib
import fcntl
import logging
import json
import os
import re
import stat
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from threading import BoundedSemaphore, Lock
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4


EVIDENCE_ROOT = Path("/opt/aios/data/authentication-evidence/telegram")
SCHEMA = "aios-telegram-owner-auth-evidence-v1"
CHALLENGE = re.compile(r"AIOS-PO-AUTH-PR([1-9][0-9]*)-[A-Za-z0-9_-]{43}", re.ASCII)
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ValueError("invalid evidence fields")


def _integer(value, minimum=None):
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError("invalid integer")


def _utc(value):
    if type(value) is not str:
        raise ValueError("invalid UTC timestamp")
    parsed = datetime.strptime(value, UTC_FORMAT).replace(tzinfo=timezone.utc)
    if parsed.strftime(UTC_FORMAT) != value:
        raise ValueError("noncanonical UTC timestamp")
    return parsed


def _timestamp(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("timezone-aware timestamp required")
    return value.astimezone(timezone.utc).strftime(UTC_FORMAT)


def validate_evidence(value):
    _keys(value, ("schema_version", "update_id", "message", "local_received_at_utc"))
    if value["schema_version"] != SCHEMA:
        raise ValueError("unsupported evidence schema")
    _integer(value["update_id"], 0)
    _utc(value["local_received_at_utc"])
    message = value["message"]
    _keys(message, ("message_id", "from", "date", "chat", "text"))
    _integer(message["message_id"], 1)
    _utc(message["date"])
    _keys(message["from"], ("id", "username"))
    _integer(message["from"]["id"], 1)
    username = message["from"]["username"]
    if username is not None and (type(username) is not str or not username):
        raise ValueError("invalid username")
    _keys(message["chat"], ("id", "type"))
    _integer(message["chat"]["id"])
    if message["chat"]["id"] == 0 or message["chat"]["type"] not in (
        "private", "group", "supergroup", "channel"
    ):
        raise ValueError("invalid chat")
    if type(message["text"]) is not str or not CHALLENGE.fullmatch(message["text"]):
        raise ValueError("not an authentication challenge")


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def decode_evidence(data):
    value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs)
    validate_evidence(value)
    if canonical_bytes(value) != data:
        raise ValueError("noncanonical evidence bytes")
    return value


class PublicationState(str, Enum):
    NOT_PUBLISHED = "NOT_PUBLISHED"
    PUBLISHED_DURABILITY_UNCERTAIN = "PUBLISHED_DURABILITY_UNCERTAIN"
    DURABLY_PUBLISHED = "DURABLY_PUBLISHED"
    COMMIT_RECOVERY_REQUIRED = "COMMIT_RECOVERY_REQUIRED"


class PublicationError(OSError):
    def __init__(self, state):
        self.state = state
        super().__init__(state.value)


def _identity(metadata):
    return [metadata.st_dev, metadata.st_ino, metadata.st_uid,
            metadata.st_gid, metadata.st_mode]


def _safe_directory(metadata, *, private):
    if not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("not a directory")
    if private:
        if metadata.st_uid != os.geteuid() or metadata.st_mode & 0o077:
            raise ValueError("archive directories must be custodian-owned and private")
    elif metadata.st_uid not in (0, os.geteuid()):
        raise ValueError("unsafe ancestor owner")
    elif metadata.st_mode & 0o022:
        # A root-owned sticky temporary ancestor protects other users' entries.
        if not (metadata.st_uid == 0 and metadata.st_mode & stat.S_ISVTX):
            raise ValueError("unsafe ancestor permissions")


_KNOWN_LAYOUTS = {}
_LAYOUT_LOCK = Lock()


@contextmanager
def _opened(name, flags, mode=0o600, *, dir_fd=None):
    """Own an opened descriptor before any metadata or stream operation."""
    fd = os.open(name, flags, mode, dir_fd=dir_fd)
    try:
        yield fd
    finally:
        try:
            os.close(fd)
        except OSError:
            pass  # Cleanup cannot change a finalized transaction outcome.


class PinnedArchive:
    """No-follow walk from /; all later I/O is relative to retained descriptors.

    An exclusive identity anchor lives in the archive's private parent, so replacing
    the archive or consumed directory cannot establish a fresh replay namespace.
    The custodian must preserve that anchor across deployments and restarts.
    """

    def __init__(self, root, *, create=False):
        self.path = Path(root)
        if not self.path.is_absolute() or ".." in self.path.parts or self.path == Path("/"):
            raise ValueError("absolute non-traversing archive path required")
        self.entries = []
        self.owned_fds = []
        with _LAYOUT_LOCK:
            known = _KNOWN_LAYOUTS.get(str(self.path))
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            fd = self.open_directory("/", flags)
            self.entries.append((None, None, fd, _identity(os.fstat(fd))))
            _safe_directory(os.fstat(fd), private=False)
            for index, name in enumerate(self.path.parts[1:]):
                private = index >= len(self.path.parts) - 3
                parent_fd = self.entries[-1][2]
                try:
                    fd = self.open_directory(name, flags, dir_fd=parent_fd)
                except FileNotFoundError:
                    if known is not None or not create:
                        raise
                    try:
                        os.mkdir(name, 0o700, dir_fd=parent_fd)
                    except FileExistsError:
                        pass
                    os.fsync(parent_fd)
                    fd = self.open_directory(name, flags, dir_fd=parent_fd)
                self.entries.append((parent_fd, name, fd, _identity(os.fstat(fd))))
                _safe_directory(os.fstat(fd), private=private)
                if known is not None and self.entries[-1][3] != known[len(self.entries) - 1]:
                    raise ValueError("previously pinned ancestor identity changed")
            self.root_fd = self.entries[-1][2]
            parent_fd = self.entries[-2][2]
            if create and known is None:
                try:
                    os.mkdir("consumed", 0o700, dir_fd=self.root_fd)
                    os.fsync(self.root_fd)
                except FileExistsError:
                    pass
            fd = self.open_directory("consumed", flags, dir_fd=self.root_fd)
            self.entries.append((self.root_fd, "consumed", fd, _identity(os.fstat(fd))))
            _safe_directory(os.fstat(fd), private=True)
            self.consumed_fd = fd
            if known is not None and self.entries[-1][3] != known[-1]:
                raise ValueError("previously pinned consumption directory identity changed")
            self.validate()
            # A previous failed initialization may have left directory entries
            # without a successful parent fsync. Existence alone is not durability.
            for _, _, directory_fd, _ in self.entries:
                os.fsync(directory_fd)
            self.validate()
            anchor = "." + self.path.name + ".auth-identity.json"
            expected = canonical_bytes({"schema_version": "aios-telegram-auth-directory-identity-v1",
                                        "identities": [entry[3] for entry in self.entries]})
            try:
                actual = self.read(parent_fd, anchor)
            except FileNotFoundError:
                if known is not None or not create:
                    raise ValueError("missing archive identity anchor") from None
                staged = self.stage(parent_fd, expected)
                try:
                    self.validate()
                    try:
                        os.link(staged, anchor, src_dir_fd=parent_fd,
                                dst_dir_fd=parent_fd, follow_symlinks=False)
                    except FileExistsError:
                        pass
                    os.fsync(parent_fd)
                    actual = self.read(parent_fd, anchor)
                finally:
                    self.cleanup(parent_fd, staged)
            if actual != expected:
                raise ValueError("archive or ancestor identity changed")
            self.validate()
            identities = [entry[3] for entry in self.entries]
            with _LAYOUT_LOCK:
                established = _KNOWN_LAYOUTS.setdefault(str(self.path), identities)
                if established != identities:
                    raise ValueError("archive layout changed during initialization")
        except BaseException:
            self.close()
            raise

    def open_directory(self, name, flags, *, dir_fd=None):
        fd = os.open(name, flags, dir_fd=dir_fd)
        self.owned_fds.append(fd)  # Registration precedes even the first fstat.
        return fd

    def validate(self):
        for parent, name, fd, identity in self.entries:
            if _identity(os.fstat(fd)) != identity:
                raise ValueError("pinned directory identity changed")
            if parent is not None:
                current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if _identity(current) != identity:
                    raise ValueError("directory entry replaced")

    def read(self, directory_fd, name):
        with _opened(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory_fd) as fd:
            before = os.fstat(fd)
            if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.geteuid()
                    or before.st_mode & 0o077):
                raise ValueError("record must be a private custodian-owned regular file")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read(65537)
            if len(data) > 65536:
                raise ValueError("record too large")
            after = os.fstat(fd)
            linked = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if (_identity(before) != _identity(after) or _identity(after) != _identity(linked)
                    or before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns):
                raise ValueError("record changed during read")
            return data

    def stage(self, directory_fd, data):
        self.validate()
        name = "." + str(uuid4()) + ".tmp"
        created = False
        try:
            with _opened(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         dir_fd=directory_fd) as fd:
                created = True
                with os.fdopen(fd, "wb", closefd=False) as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(fd)
            self.validate()
            return name
        except BaseException:
            if created:
                self.cleanup(directory_fd, name)
            raise

    def current_objects(self, directory_fd, objects):
        """Validate the pinned chain and the returned names' exact linked objects."""
        self.validate()
        for name, identity in objects.items():
            current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if _identity(current) != identity:
                raise ValueError("committed object replaced or missing")
        self.validate()

    @staticmethod
    def cleanup(directory_fd, name):
        if name is not None:
            try:
                os.unlink(name, dir_fd=directory_fd)
            except OSError:
                # Cleanup never changes the publication outcome or removes evidence.
                pass

    def close(self):
        for fd in reversed(self.owned_fds):
            try:
                os.close(fd)
            except OSError:
                pass
        self.entries = []
        self.owned_fds = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _completion(name, data):
    return canonical_bytes({"schema_version": "aios-telegram-auth-publication-v1",
                            "filename": name,
                            "transport_sha256": hashlib.sha256(data).hexdigest(),
                            "state": PublicationState.DURABLY_PUBLISHED.value})


def _attempt_record(name, data, state):
    return canonical_bytes({"schema_version": "aios-telegram-auth-attempt-v1",
                            "filename": name,
                            "transport_sha256": hashlib.sha256(data).hexdigest(),
                            "state": state})


def _append_attempt(fd, name, data, state):
    line = _attempt_record(name, data, state)
    os.lseek(fd, 0, os.SEEK_END)
    view = memoryview(line)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("attempt journal write failed")
        view = view[written:]
    os.fsync(fd)


def _pending_guard(directory_fd, name, data):
    try:
        with _opened(name + ".pending", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     dir_fd=directory_fd) as fd:
            with os.fdopen(fd, "wb", closefd=False) as stream:
                stream.write(_attempt_record(name, data, "PENDING"))
                stream.flush()
                os.fsync(fd)
        os.fsync(directory_fd)
    except FileExistsError:
        # Any existing guard denies verification; do not overwrite it.
        pass


def _reject_uncertain(fd, name, data):
    # Diagnostic only: absence of a final marker is the durable denial. No
    # quarantine write, transient lock or process-local memory enables safety.
    try:
        _append_attempt(fd, name, data, "UNCERTAIN")
    except OSError:
        logging.getLogger(__name__).error(
            "Telegram auth provisional attempt failed; no final commit published")


def _commit_record(archive, directory_fd, name, data, committed_at):
    """Construct the exact closed commit schema from pinned, validated objects."""
    _utc(committed_at)
    payload = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs)
    if payload.get("schema_version") == SCHEMA:
        validate_evidence(payload)
        sender = payload["message"]["from"]["id"]
        challenge_digest = hashlib.sha256(payload["message"]["text"].encode("utf-8")).hexdigest()
    else:
        if payload.get("schema_version") != "aios-telegram-owner-auth-consumption-v1":
            raise ValueError("unsupported commit payload")
        sender = payload["telegram_user_id"]
        challenge_digest = payload["challenge_sha256"]
    expected = {
        "evidence": (name, data),
        "certificate": (name + ".complete", _completion(name, data)),
        "journal": (name + ".attempt", _attempt_record(name, data, "PENDING")
                    + _attempt_record(name, data, "PREPARED")),
        "guard": (name + ".pending", _attempt_record(name, data, "PENDING")),
    }
    objects = {}
    for role, (filename, raw) in expected.items():
        if archive.read(directory_fd, filename) != raw:
            raise ValueError("attempt completion object digest/state mismatch")
        objects[role] = {"filename": filename,
                         "identity": _identity(os.stat(filename, dir_fd=directory_fd,
                                                        follow_symlinks=False)),
                         "sha256": hashlib.sha256(raw).hexdigest()}
    archive.current_objects(directory_fd, {obj["filename"]: obj["identity"]
                                           for obj in objects.values()})
    return {"schema_version": "aios-telegram-auth-commit-v1", "state": "COMMITTED",
            "attempt_id": name, "challenge_sha256": challenge_digest,
            "telegram_user_id": sender, "committed_at_utc": committed_at,
            "directory_identity": _identity(os.fstat(directory_fd)),
            "namespace_identities": [entry[3] for entry in archive.entries],
            "objects": objects}


def _recover_commit(archive, directory_fd, name, data):
    """Accept only an existing final decision; finish durability after interruption.

    A surviving link does not prove that the publisher's directory fsync returned.
    Reopen validates every binding and repeats fsyncs before exposing eligibility.
    Recovery NEVER creates a marker or promotes provisional artifacts.
    """
    marker = name + ".commit"
    try:
        raw = archive.read(directory_fd, marker)
    except FileNotFoundError:
        raise ValueError("attempt has no final commit marker") from None
    record = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    if type(record) is not dict:
        raise ValueError("invalid commit record")
    expected = _commit_record(archive, directory_fd, name, data,
                              record.get("committed_at_utc"))
    if raw != canonical_bytes(expected):
        raise ValueError("commit record identity/digest/schema mismatch")
    identities = {obj["filename"]: obj["identity"] for obj in expected["objects"].values()}
    identities[marker] = _identity(os.stat(marker, dir_fd=directory_fd, follow_symlinks=False))
    for filename, identity in identities.items():
        with _opened(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory_fd) as fd:
            if _identity(os.fstat(fd)) != identity:
                raise ValueError("commit object replaced during recovery")
            os.fsync(fd)
    os.fsync(directory_fd)
    archive.current_objects(directory_fd, identities)
    # Recheck bound bytes as well as inodes after the recovery durability barrier.
    if archive.read(directory_fd, marker) != raw or canonical_bytes(
            _commit_record(archive, directory_fd, name, data,
                           expected["committed_at_utc"])) != raw:
        raise ValueError("commit changed during recovery")


@contextmanager
def _committed_attempt(archive, directory_fd, name, data):
    # Lock only serializes with an in-flight publisher. Correctness after process
    # death derives from the final marker and retained bindings, never this lock.
    with _opened(name + ".attempt", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                 dir_fd=directory_fd) as fd:
        fcntl.flock(fd, fcntl.LOCK_SH)
        metadata = os.fstat(fd)
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.geteuid()
                or metadata.st_mode & 0o077):
            raise ValueError("unsafe attempt journal")
        _recover_commit(archive, directory_fd, name, data)
        yield


def _publish(archive, directory_fd, name, data):
    """Prepare immutable artifacts, then publish one irreversible final decision."""
    attempt_name = name + ".attempt"
    try:
        os.stat(name + ".complete", dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        pass
    else:
        raise FileExistsError("completion namespace already reserved")
    with _opened(attempt_name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 dir_fd=directory_fd) as attempt_fd:
        fcntl.flock(attempt_fd, fcntl.LOCK_EX)
        payload_stage = completion_stage = None
        state = PublicationState.NOT_PUBLISHED
        objects = {}
        committing = False
        try:
            objects = {attempt_name: _identity(os.fstat(attempt_fd))}
            _append_attempt(attempt_fd, name, data, "PENDING")
            _pending_guard(directory_fd, name, data)
            os.fsync(directory_fd)
            payload_stage = archive.stage(directory_fd, data)
            completion_stage = archive.stage(directory_fd, _completion(name, data))
            objects[name] = _identity(os.stat(payload_stage, dir_fd=directory_fd, follow_symlinks=False))
            objects[name + ".complete"] = _identity(os.stat(completion_stage, dir_fd=directory_fd, follow_symlinks=False))
            archive.validate()
            try:
                os.link(payload_stage, name, src_dir_fd=directory_fd,
                        dst_dir_fd=directory_fd, follow_symlinks=False)
            except OSError:
                try:
                    if _identity(os.stat(name, dir_fd=directory_fd, follow_symlinks=False)) == objects[name]:
                        state = PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
                except FileNotFoundError:
                    pass
                except OSError:
                    state = PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
                raise
            state = PublicationState.PUBLISHED_DURABILITY_UNCERTAIN
            os.fsync(directory_fd)
            if archive.read(directory_fd, name) != data:
                raise ValueError("published bytes failed verification")
            archive.validate()  # Immediately before completion publication.
            os.link(completion_stage, name + ".complete", src_dir_fd=directory_fd,
                    dst_dir_fd=directory_fd, follow_symlinks=False)
            archive.current_objects(directory_fd, objects)  # Immediately after.
            os.fsync(directory_fd)
            if archive.read(directory_fd, name + ".complete") != _completion(name, data):
                raise ValueError("completion readback failed")
            archive.current_objects(directory_fd, objects)
            # Required transaction cleanup happens before final state. A failure
            # here is uncertain too; never suppress an observed post-link error.
            os.unlink(payload_stage, dir_fd=directory_fd)
            payload_stage = None
            os.unlink(completion_stage, dir_fd=directory_fd)
            completion_stage = None
            os.fsync(directory_fd)
            _append_attempt(attempt_fd, name, data, "PREPARED")
            # The guard is permanent and bound by the final marker. There is no
            # retirement window and no mutable COMMITTED journal entry.
            record = _commit_record(archive, directory_fd, name, data,
                                    _timestamp(datetime.now(timezone.utc)))
            commit_stage = archive.stage(directory_fd, canonical_bytes(record))
            archive.current_objects(directory_fd, objects)
            if canonical_bytes(_commit_record(archive, directory_fd, name, data,
                                               record["committed_at_utc"])) != canonical_bytes(record):
                raise ValueError("commit bindings changed before publication")
            # Irreversible decision boundary. Any ambiguous error from here is
            # RECOVERY_REQUIRED, never an uncertain/aborted attempt later promoted.
            committing = True
            os.link(commit_stage, name + ".commit", src_dir_fd=directory_fd,
                    dst_dir_fd=directory_fd, follow_symlinks=False)
            _recover_commit(archive, directory_fd, name, data)
            # The marker staging alias is deliberately retained. No fallible
            # security-critical cleanup follows the durable decision.
        except BaseException as error:
            if committing:
                state = PublicationState.COMMIT_RECOVERY_REQUIRED
            else:
                _reject_uncertain(attempt_fd, name, data)
            if isinstance(error, FileExistsError) and state == PublicationState.NOT_PUBLISHED:
                raise
            if not isinstance(error, Exception):
                raise
            raise PublicationError(state) from None
        # On failure retain any remaining staging aliases alongside the final
        # artifacts and terminal state for inspection. Do not retry publication.


def _store(data, root):
    digest = hashlib.sha256(data).hexdigest()
    name = f"{uuid4()}.{digest}.json"
    try:
        with PinnedArchive(root, create=True) as archive:
            _publish(archive, archive.root_fd, name, data)
    except PublicationError:
        raise
    except (OSError, ValueError):
        raise PublicationError(PublicationState.NOT_PUBLISHED) from None
    return Path(root) / name


def _project_update(update, received_at=None):
    """Project only allowlisted platform fields; ignore all unrelated messages."""
    message = getattr(update, "message", None)
    text = getattr(message, "text", None)
    if type(text) is not str or not CHALLENGE.fullmatch(text):
        return None
    try:
        record = {
            "schema_version": SCHEMA,
            "update_id": update.update_id,
            "local_received_at_utc": _timestamp(received_at or datetime.now(timezone.utc)),
            "message": {
                "message_id": message.message_id,
                "from": {"id": message.from_user.id,
                         "username": getattr(message.from_user, "username", None)},
                "date": _timestamp(message.date),
                "chat": {"id": message.chat.id, "type": message.chat.type},
                "text": text,
            },
        }
    except AttributeError:
        raise ValueError("incomplete Telegram update") from None
    validate_evidence(record)
    data = canonical_bytes(record)
    return data


def retain_update(update, *, root=EVIDENCE_ROOT, received_at=None):
    data = _project_update(update, received_at)
    return None if data is None else _store(data, root)


class CaptureDispatcher:
    """One running capture, zero waiting jobs; the handler never waits on disk."""

    def __init__(self, root=EVIDENCE_ROOT):
        self.root = root
        self.slot = BoundedSemaphore(1)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="telegram-auth-evidence")

    def submit(self, update):
        try:
            # Snapshot exact allowlisted fields on the event loop BEFORE normalization.
            data = _project_update(update)
        except (ValueError, TypeError, OverflowError):
            logging.getLogger(__name__).error("Telegram auth capture NOT_PUBLISHED: invalid update")
            return "NOT_PUBLISHED"
        if data is None:
            return "NOT_AUTH"
        if not self.slot.acquire(blocking=False):
            logging.getLogger(__name__).error("Telegram auth capture NOT_PUBLISHED: capacity exhausted")
            return "REJECTED_CAPACITY"
        try:
            future = self.executor.submit(_store, data, self.root)
        except RuntimeError:
            # submit() may enqueue before failing to start its worker. Permanently
            # close/cancel that executor so repeated failures cannot grow a queue.
            self.executor.shutdown(wait=False, cancel_futures=True)
            self.slot.release()
            logging.getLogger(__name__).error("Telegram auth capture NOT_PUBLISHED: worker unavailable")
            return "NOT_PUBLISHED"
        future.add_done_callback(self._finished)
        return "ADMITTED"

    def _finished(self, future):
        try:
            future.result()
        except PublicationError as error:
            logging.getLogger(__name__).error("Telegram auth capture %s", error.state.value)
        except Exception:
            logging.getLogger(__name__).error("Telegram auth capture failed: inspect retained evidence")
        else:
            logging.getLogger(__name__).info("Telegram auth capture DURABLY_PUBLISHED")
        finally:
            self.slot.release()

    def close(self):
        self.executor.shutdown(wait=True)


CAPTURE_DISPATCHER = CaptureDispatcher()


@dataclass(frozen=True)
class ChallengeBinding:
    """Trusted, previously issued challenge; never derive this from a received update."""

    text: str
    pr_number: int
    head: str
    approval_record_id: str
    expected_sender_id: int
    expected_username: str
    created_at_utc: str
    expires_at_utc: str


def verify_and_consume(evidence_path, challenge, *, root=EVIDENCE_ROOT, verified_at=None):
    """Explicit operator call, never called by ingestion. Raises on any failed check.

    The root must be the trusted receiver archive, not user-supplied JSON storage.
    Old normalized manifests cannot pass decode_evidence. A permanent no-replace
    marker is the replay guard; preserve it across restarts and deployments.
    """
    root = Path(root)
    path = Path(evidence_path)
    if path.parent != root or path.name in (".", ".."):
        raise ValueError("evidence must be in the trusted receiver archive")
    with PinnedArchive(root) as archive:
        return _verify_pinned(archive, path, challenge, verified_at)


def _verify_pinned(archive, path, challenge, verified_at):
    data = archive.read(archive.root_fd, path.name)
    with _committed_attempt(archive, archive.root_fd, path.name, data):
        return _verify_committed(archive, path, data, challenge, verified_at)


def _verify_committed(archive, path, data, challenge, verified_at):
    certificate = archive.read(archive.root_fd, path.name + ".complete")
    if certificate != _completion(path.name, data):
        raise ValueError("evidence lacks successful durability completion")
    archive.validate()
    evidence = decode_evidence(data)
    digest = hashlib.sha256(data).hexdigest()
    parts = path.name.split(".")
    if len(parts) != 3 or parts[1:] != [digest, "json"] or str(UUID(parts[0])) != parts[0]:
        raise ValueError("transport digest/filename mismatch")
    match = CHALLENGE.fullmatch(challenge.text)
    _integer(challenge.pr_number, 1)
    _integer(challenge.expected_sender_id, 1)
    if (match is None or int(match[1]) != challenge.pr_number
            or re.fullmatch(r"[0-9a-f]{40}", challenge.head) is None
            or str(UUID(challenge.approval_record_id)) != challenge.approval_record_id
            or type(challenge.expected_username) is not str or not challenge.expected_username):
        raise ValueError("invalid trusted challenge binding")
    start = _utc(challenge.created_at_utc)
    end = _utc(challenge.expires_at_utc)
    message = evidence["message"]
    received = _utc(evidence["local_received_at_utc"])
    sent = _utc(message["date"])
    checked = _timestamp(verified_at or datetime.now(timezone.utc))
    # Telegram dates have second precision; local receipt must still be >= issue time.
    if not (start < end and start <= received <= end
            and start.replace(microsecond=0) <= sent <= received
            and received <= _utc(checked)):
        raise ValueError("challenge timestamp outside validity window")
    sender = message["from"]
    if (message["text"] != challenge.text
            or sender["id"] != challenge.expected_sender_id
            or sender["username"] not in (None, challenge.expected_username)
            or message["chat"] != {"id": sender["id"], "type": "private"}):
        raise ValueError("challenge or sender mismatch")
    receipt = {
        "schema_version": "aios-telegram-owner-auth-consumption-v1",
        "status": "consumed",
        "purpose": "Project Owner Telegram channel authentication",
        "pr_number": challenge.pr_number,
        "head": challenge.head,
        "approval_record_id": challenge.approval_record_id,
        "challenge_created_at_utc": challenge.created_at_utc,
        "challenge_expires_at_utc": challenge.expires_at_utc,
        "challenge_sha256": hashlib.sha256(challenge.text.encode("utf-8")).hexdigest(),
        "evidence_filename": path.name,
        "evidence_transport_sha256": digest,
        "telegram_user_id": sender["id"],
        "telegram_username": sender["username"],
        "declared_display_username": challenge.expected_username,
        "verified_at_utc": checked,
        "role_context": {
            "mode": "solo-project-owner-bootstrap",
            "combined_roles": ["reviewer", "approver", "custodian", "commissioner"],
            "disclosure": "Solo-owner self-verification, not independent human corroboration. AI assistance is advisory only.",
        },
    }
    # One permanent marker per challenge, even for different updates or duplicate captures.
    name = receipt["challenge_sha256"] + ".json"
    _publish(archive, archive.consumed_fd, name, canonical_bytes(receipt))
    return archive.path / "consumed" / name
