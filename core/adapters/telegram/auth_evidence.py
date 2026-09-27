"""Bounded Telegram challenge capture; capture alone never authenticates an Owner."""

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
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


def _directory(path):
    if path.is_symlink():
        raise ValueError("evidence directory must be a real directory")
    if not path.exists():
        if not path.parent.exists():
            _directory(path.parent)
        path.mkdir(mode=0o700, exist_ok=True)
        # Persist newly created directory entries as well as their later contents.
        parent_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("evidence directory must be a real directory")
    if path.stat().st_uid != os.geteuid() or path.stat().st_mode & 0o022:
        raise ValueError("evidence directory must be owned and writable only by its custodian")


def _publish(directory, name, data):
    """Publish complete fsynced bytes with an atomic no-replace hard link."""
    _directory(directory)
    temporary = directory / ("." + str(uuid4()) + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        destination = directory / name
        os.link(temporary, destination)  # EEXIST is never an overwrite.
        temporary.unlink()
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return destination
    finally:
        temporary.unlink(missing_ok=True)


def retain_update(update, *, root=EVIDENCE_ROOT, received_at=None):
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
    digest = hashlib.sha256(data).hexdigest()
    # The filename retains the transport digest without a circular self-hash.
    return _publish(Path(root), f"{uuid4()}.{digest}.json", data)


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
    if (path.parent != root or root.is_symlink() or not root.is_dir()
            or root.stat().st_uid != os.geteuid() or root.stat().st_mode & 0o022):
        raise ValueError("evidence must be in the trusted receiver archive")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.geteuid()
                or metadata.st_mode & 0o022):
            raise ValueError("evidence must be a custodian-owned regular file")
        data = stream.read()
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
    return _publish(root / "consumed", receipt["challenge_sha256"] + ".json",
                    canonical_bytes(receipt))
