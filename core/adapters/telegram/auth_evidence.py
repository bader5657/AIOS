"""Bounded Telegram challenge capture; capture alone never authenticates an Owner."""

import hashlib
import logging
import json
import os
import re
import stat
from concurrent.futures import ThreadPoolExecutor
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
        with _LAYOUT_LOCK:
            known = _KNOWN_LAYOUTS.get(str(self.path))
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            fd = os.open("/", flags)
            self.entries.append((None, None, fd, _identity(os.fstat(fd))))
            _safe_directory(os.fstat(fd), private=False)
            for index, name in enumerate(self.path.parts[1:]):
                private = index >= len(self.path.parts) - 3
                parent_fd = self.entries[-1][2]
                try:
                    fd = os.open(name, flags, dir_fd=parent_fd)
                except FileNotFoundError:
                    if known is not None or not create:
                        raise
                    try:
                        os.mkdir(name, 0o700, dir_fd=parent_fd)
                    except FileExistsError:
                        pass
                    os.fsync(parent_fd)
                    fd = os.open(name, flags, dir_fd=parent_fd)
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
            fd = os.open("consumed", flags, dir_fd=self.root_fd)
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

    def validate(self):
        for parent, name, fd, identity in self.entries:
            if _identity(os.fstat(fd)) != identity:
                raise ValueError("pinned directory identity changed")
            if parent is not None:
                current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if _identity(current) != identity:
                    raise ValueError("directory entry replaced")

    def read(self, directory_fd, name):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory_fd)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.geteuid()
                    or before.st_mode & 0o077):
                raise ValueError("record must be a private custodian-owned regular file")
            data = stream.read(65537)
            if len(data) > 65536:
                raise ValueError("record too large")
            after = os.fstat(stream.fileno())
            linked = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if (_identity(before) != _identity(after) or _identity(after) != _identity(linked)
                    or before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns):
                raise ValueError("record changed during read")
            return data

    def stage(self, directory_fd, data):
        self.validate()
        name = "." + str(uuid4()) + ".tmp"
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory_fd)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            self.validate()
            return name
        except BaseException:
            self.cleanup(directory_fd, name)
            raise

    @staticmethod
    def cleanup(directory_fd, name):
        if name is not None:
            try:
                os.unlink(name, dir_fd=directory_fd)
            except OSError:
                # Cleanup never changes the publication outcome or removes evidence.
                pass

    def close(self):
        for _, _, fd, _ in reversed(self.entries):
            try:
                os.close(fd)
            except OSError:
                pass
        self.entries = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _completion(name, data):
    return canonical_bytes({"schema_version": "aios-telegram-auth-publication-v1",
                            "filename": name,
                            "transport_sha256": hashlib.sha256(data).hexdigest(),
                            "state": PublicationState.DURABLY_PUBLISHED.value})


def _publish(archive, directory_fd, name, data):
    """The completion link is the final commit point, AFTER required fsyncs.

    Its absence always rejects verification. Its survival is not required for
    safety: a lost completion link denies authentication rather than promoting
    uncertain data. No fallible durability operation follows that commit point.
    """
    payload_stage = completion_stage = None
    state = PublicationState.NOT_PUBLISHED
    try:
        try:
            os.stat(name + ".complete", dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise FileExistsError("completion namespace already reserved")
        payload_stage = archive.stage(directory_fd, data)
        completion_stage = archive.stage(directory_fd, _completion(name, data))
        archive.validate()
        try:
            os.link(payload_stage, name, src_dir_fd=directory_fd,
                    dst_dir_fd=directory_fd, follow_symlinks=False)
        except OSError:
            # A failed publication call can have an uncertain outcome. Attribute
            # any surviving link to this staged inode, not a pre-existing record.
            try:
                linked = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                staged = os.stat(payload_stage, dir_fd=directory_fd, follow_symlinks=False)
                if _identity(linked) == _identity(staged):
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
        archive.validate()
        # All payload durability and identity checks have succeeded. Publishing
        # this already-fsynced certificate is the last fallible operation.
        os.link(completion_stage, name + ".complete", src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd, follow_symlinks=False)
    except FileExistsError:
        if state == PublicationState.NOT_PUBLISHED:
            raise  # Includes replay; never replace the existing marker.
        raise PublicationError(state) from None
    except (OSError, ValueError):
        raise PublicationError(state) from None
    finally:
        archive.cleanup(directory_fd, payload_stage)
        archive.cleanup(directory_fd, completion_stage)


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
