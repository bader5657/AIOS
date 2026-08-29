"""Fail-closed Stage 0.33C candidate-create authorization boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
import grp
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Callable, NoReturn
from uuid import UUID


from .candidate_input import (
    IngestionResult,
    TrustedReceiptFacts,
    TrustedReceiptItemFacts,
    source_context_from_ingestion_result,
)


AUTHORIZATION_PATH = Path(
    "/opt/aios/runtime/intelligence/production-candidate-create/"
    "stage-0.33c/authorization.json"
)
CONSUMPTION_DIRECTORY = Path(
    "/opt/aios/runtime/intelligence/production-candidate-create/"
    "stage-0.33c/consumed"
)
AUTHORIZATION_SCHEMA_VERSION = (
    "aios-stage-0.33c-candidate-create-authorization-v1"
)
CONSUMPTION_SCHEMA_VERSION = (
    "aios-stage-0.33c-candidate-create-consumption-v1"
)
MAX_AUTHORIZATION_BYTES = 16_384
MAX_MANIFEST_BYTES = 4_194_304
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SESSION = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}")
_AUTHORIZATION_FIELDS = frozenset(
    {
        "schema_version",
        "enabled",
        "authorization_id",
        "not_before_utc",
        "expires_at_utc",
        "max_requests",
        "operator_actor_reference",
        "source_manifest_reference",
        "source_manifest_sha256",
        "trusted_facts_sha256",
        "evidence_session_id",
    }
)


class CandidateCreateControlFailureCode(str, Enum):
    AUTHORIZATION_DISABLED = "AUTHORIZATION_DISABLED"
    AUTHORIZATION_INVALID = "AUTHORIZATION_INVALID"
    AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"
    AUTHORIZATION_ACTOR_INVALID = "AUTHORIZATION_ACTOR_INVALID"
    AUTHORIZATION_BINDING_INVALID = "AUTHORIZATION_BINDING_INVALID"
    AUTHORIZATION_CONSUMED = "AUTHORIZATION_CONSUMED"
    AUTHORIZATION_CONSUMPTION_STATE_INVALID = (
        "AUTHORIZATION_CONSUMPTION_STATE_INVALID"
    )
    AUTHORIZATION_DURABILITY_FAILED = "AUTHORIZATION_DURABILITY_FAILED"


class CandidateCreateControlError(Exception):
    """Bounded control-plane failure without path, payload, or secret detail."""

    __slots__ = ("code",)

    def __init__(self, code: CandidateCreateControlFailureCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class AuthorizationBoundary:
    """Filesystem policy; production defaults are fixed and fail closed."""

    authorization_path: Path
    consumption_directory: Path
    authorization_uid: int
    authorization_gid: int
    runtime_uid: int
    runtime_gid: int

    @classmethod
    def production(cls) -> AuthorizationBoundary:
        try:
            authorization_gid = grp.getgrnam("aiosadmin").gr_gid
        except KeyError:
            _fail(CandidateCreateControlFailureCode.AUTHORIZATION_INVALID)
        return cls(
            AUTHORIZATION_PATH,
            CONSUMPTION_DIRECTORY,
            0,
            authorization_gid,
            os.geteuid(),
            os.getegid(),
        )


@dataclass(frozen=True, slots=True)
class AuthorizationClaim:
    authorization_id: str
    authorization_artifact_sha256: str
    operator_actor_reference: str
    source_evidence_sha256: str
    correlation_id: str
    consumption_path: Path
    consumed_at_utc: str


def _fail(code: CandidateCreateControlFailureCode) -> NoReturn:
    raise CandidateCreateControlError(code) from None


def _duplicates_rejected(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _bounded_regular_bytes(
    path: Path,
    *,
    maximum: int,
    uid: int | None,
    gid: int | None,
    mode: int | None,
) -> bytes:
    descriptor: int | None = None
    try:
        metadata = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("not regular")
        if uid is not None and metadata.st_uid != uid:
            raise OSError("owner")
        if gid is not None and metadata.st_gid != gid:
            raise OSError("group")
        if mode is not None and stat.S_IMODE(metadata.st_mode) != mode:
            raise OSError("mode")
        if metadata.st_size > maximum:
            raise OSError("size")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
            raise OSError("changed")
        chunks: list[bytes] = []
        remaining = maximum + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > maximum:
            raise OSError("size")
        return raw
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _require_real_path_components(path: Path) -> None:
    if not path.is_absolute():
        raise OSError("path must be absolute")
    current = Path(path.anchor)
    for component in path.parts[1:-1]:
        current /= component
        metadata = os.stat(current, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode):
            raise OSError("unsafe path component")


def _canonical_uuid4(value: object) -> str:
    if type(value) is not str or len(value) != 36:
        raise ValueError("uuid")
    parsed = UUID(value)
    if parsed.version != 4 or str(parsed) != value:
        raise ValueError("uuid")
    return value


def _canonical_utc(value: object) -> datetime:
    if type(value) is not str or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ):
        raise ValueError("timestamp")
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ValueError("timestamp")
    return parsed


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value, "f")


def _item_value(item: TrustedReceiptItemFacts) -> dict[str, object]:
    return {
        "line_number": item.line_number,
        "candidate_material_description": item.candidate_material_description,
        "canonical_display_name": item.canonical_display_name,
        "size_description": item.size_description,
        "specification": item.specification,
        "material_id": str(item.material_id) if item.material_id else None,
        "full_colly_count": item.full_colly_count,
        "qty_per_full_colly": _decimal_text(item.qty_per_full_colly),
        "partial_qty": _decimal_text(item.partial_qty),
        "total_qty": _decimal_text(item.total_qty),
        "unit": item.unit,
    }


def trusted_facts_sha256(facts: TrustedReceiptFacts) -> str:
    """Hash the exact validated, canonical governed facts representation."""

    validated = TrustedReceiptFacts.validate(facts)
    value = {
        "supplier_name": validated.supplier_name,
        "document_number": validated.document_number,
        "document_date": (
            validated.document_date.isoformat() if validated.document_date else None
        ),
        "received_at": validated.received_at.isoformat(),
        "items": [_item_value(item) for item in validated.items],
    }
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _authorization(
    boundary: AuthorizationBoundary,
) -> tuple[dict[str, object], bytes, str]:
    try:
        _require_real_path_components(boundary.authorization_path)
        raw = _bounded_regular_bytes(
            boundary.authorization_path,
            maximum=MAX_AUTHORIZATION_BYTES,
            uid=boundary.authorization_uid,
            gid=boundary.authorization_gid,
            mode=0o440,
        )
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_duplicates_rejected)
    except FileNotFoundError:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_DISABLED)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_INVALID)
    if type(value) is not dict or set(value) != _AUTHORIZATION_FIELDS:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_INVALID)
    return value, raw, hashlib.sha256(raw).hexdigest()


def _safe_consumed_marker(path: Path, boundary: AuthorizationBoundary) -> bool:
    try:
        metadata = os.stat(path, follow_symlinks=False)
    except OSError:
        return False
    return (
        stat.S_ISREG(metadata.st_mode)
        and metadata.st_uid == boundary.runtime_uid
        and metadata.st_gid == boundary.runtime_gid
        and stat.S_IMODE(metadata.st_mode) == 0o600
    )


def _validate_consumption_directory(boundary: AuthorizationBoundary) -> None:
    try:
        _require_real_path_components(boundary.consumption_directory / "marker")
        metadata = os.stat(boundary.consumption_directory, follow_symlinks=False)
    except OSError:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_INVALID)
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or metadata.st_uid != boundary.runtime_uid
        or metadata.st_gid != boundary.runtime_gid
        or stat.S_IMODE(metadata.st_mode) & 0o022
    ):
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_INVALID)


def _write_all(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(descriptor, payload[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def _claim(
    boundary: AuthorizationBoundary,
    *,
    authorization_id: str,
    artifact_sha256: str,
    operator_reference: str,
    source_sha256: str,
    correlation_id: str,
    now: datetime,
) -> AuthorizationClaim:
    _validate_consumption_directory(boundary)
    path = boundary.consumption_directory / f"{authorization_id}.json"
    descriptor: int | None = None
    try:
        try:
            descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
            )
            created = os.fstat(descriptor)
            if (
                not stat.S_ISREG(created.st_mode)
                or created.st_uid != boundary.runtime_uid
                or created.st_gid != boundary.runtime_gid
                or stat.S_IMODE(created.st_mode) != 0o600
            ):
                _fail(
                    CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMPTION_STATE_INVALID
                )
        except FileExistsError:
            if _safe_consumed_marker(path, boundary):
                _fail(CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMED)
            _fail(
                CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMPTION_STATE_INVALID
            )
        consumed_at = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        record = {
            "schema_version": CONSUMPTION_SCHEMA_VERSION,
            "authorization_id": authorization_id,
            "authorization_artifact_sha256": artifact_sha256,
            "consumed_at_utc": consumed_at,
            "operator_reference": operator_reference,
            "source_evidence_sha256": source_sha256,
            "correlation_id": correlation_id,
            "state": "CONSUMED",
        }
        payload = (
            json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        _write_all(descriptor, payload)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        directory_descriptor = os.open(
            boundary.consumption_directory,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        return AuthorizationClaim(
            authorization_id,
            artifact_sha256,
            operator_reference,
            source_sha256,
            correlation_id,
            path,
            consumed_at,
        )
    except CandidateCreateControlError:
        raise
    except OSError:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_DURABILITY_FAILED)
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def authorize_and_consume_candidate_create(
    ingestion_result: IngestionResult,
    trusted_facts: TrustedReceiptFacts,
    *,
    boundary: AuthorizationBoundary | None = None,
    clock: Callable[[], datetime] | None = None,
) -> AuthorizationClaim:
    """Validate all deterministic eligibility and durably consume once."""

    if type(ingestion_result) is not IngestionResult:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_BINDING_INVALID)
    if type(trusted_facts) is not TrustedReceiptFacts:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_BINDING_INVALID)
    try:
        TrustedReceiptFacts.validate(trusted_facts)
        source = source_context_from_ingestion_result(ingestion_result)
    except Exception:
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_BINDING_INVALID)
    current_boundary = boundary or AuthorizationBoundary.production()
    value, raw, artifact_sha256 = _authorization(current_boundary)
    del raw
    try:
        if value["schema_version"] != AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("schema")
        authorization_id = _canonical_uuid4(value["authorization_id"])
        if value["enabled"] is not True or type(value["max_requests"]) is not int or value["max_requests"] != 1:
            _fail(CandidateCreateControlFailureCode.AUTHORIZATION_DISABLED)
        not_before = _canonical_utc(value["not_before_utc"])
        expires = _canonical_utc(value["expires_at_utc"])
        now = (clock or (lambda: datetime.now(timezone.utc)))()
        if type(now) is not datetime or now.tzinfo is None:
            raise ValueError("clock")
        now = now.astimezone(timezone.utc)
        if expires <= not_before or now < not_before or now >= expires:
            _fail(CandidateCreateControlFailureCode.AUTHORIZATION_EXPIRED)
        operator = value["operator_actor_reference"]
        if type(operator) is not str or not operator.startswith("operator:"):
            _fail(CandidateCreateControlFailureCode.AUTHORIZATION_ACTOR_INVALID)
        if _canonical_uuid4(operator.removeprefix("operator:")) != operator[9:]:
            raise ValueError("actor")
        manifest_reference = value["source_manifest_reference"]
        source_digest = value["source_manifest_sha256"]
        facts_digest = value["trusted_facts_sha256"]
        correlation_id = value["evidence_session_id"]
        if (
            type(manifest_reference) is not str
            or manifest_reference != source.manifest_reference
            or type(source_digest) is not str
            or not _SHA256.fullmatch(source_digest)
            or type(facts_digest) is not str
            or not _SHA256.fullmatch(facts_digest)
            or type(correlation_id) is not str
            or not _SESSION.fullmatch(correlation_id)
        ):
            raise ValueError("binding")
        manifest_raw = _bounded_regular_bytes(
            Path(manifest_reference),
            maximum=MAX_MANIFEST_BYTES,
            uid=None,
            gid=None,
            mode=None,
        )
        if (
            hashlib.sha256(manifest_raw).hexdigest() != source_digest
            or trusted_facts_sha256(trusted_facts) != facts_digest
        ):
            _fail(CandidateCreateControlFailureCode.AUTHORIZATION_BINDING_INVALID)
    except CandidateCreateControlError:
        raise
    except (KeyError, TypeError, ValueError, OSError):
        _fail(CandidateCreateControlFailureCode.AUTHORIZATION_INVALID)
    return _claim(
        current_boundary,
        authorization_id=authorization_id,
        artifact_sha256=artifact_sha256,
        operator_reference=operator,
        source_sha256=source_digest,
        correlation_id=correlation_id,
        now=now,
    )
