"""Ephemeral Stage 0.33C one-shot controlled candidate-create harness."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import threading
import unicodedata
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Awaitable, Callable, NoReturn
from uuid import UUID

from core.app.input_classifier import InputType
from core.event import EventDeliveryFailureCode
from core.material_receipts.models import ReceiptForReview, ReceiptStatus

from .candidate_create_authorization import (
    CandidateCreateControlError,
    CandidateCreateControlFailureCode,
)
from .candidate_input import IngestionResult, TrustedReceiptFacts, TrustedReceiptItemFacts
from .candidate_input_errors import CandidateInputError, CandidateInputFailureCode
from .controlled_candidate_create import (
    ControlledCandidateCreateRequest,
    controlled_create_review_candidate,
)
from .results import ReviewApplicationError, ReviewFailureCode


MAX_SEMANTIC_INPUT_BYTES = 4_255_677
MAX_TRANSPORT_INPUT_BYTES = 4_255_678
MAX_OUTPUT_BYTES = 4_096
CATASTROPHIC_STDERR = b"AIOS_STAGE_0_33C_HARNESS_BOUNDARY_FAILURE\n"

_SCHEMA_VERSION = "aios-stage-0.33c-one-shot-input-v1"
_RESULT_SCHEMA_VERSION = "aios-stage-0.33c-one-shot-result-v1"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{0,5}[1-9])?\Z")
_MANIFEST = re.compile(
    r"/opt/aios/data/documents/manifests/"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json\Z"
)
_UNUSED = "UNUSED"
_CLAIMED = "CLAIMED"
_state = _UNUSED
_claim_lock = threading.Lock()

_TOP_FIELDS = frozenset(
    {"schema_version", "ingestion_result", "trusted_receipt_facts"}
)
_INGESTION_FIELDS = frozenset(
    {
        "input_type",
        "recognized_input_type",
        "stored_path",
        "manifest_path",
        "metadata",
        "text",
        "register_handoff_ready",
        "process_handoff_ready",
        "route_handoff_ready",
        "respond_acknowledgement_ready",
        "registration_succeeded",
        "registry_record_id",
        "event_publication_attempted",
        "event_delivery_succeeded",
        "event_delivery_failure_code",
        "brain_result",
    }
)
_FACT_FIELDS = frozenset(
    {"supplier_name", "document_number", "document_date", "received_at", "items"}
)
_ITEM_FIELDS = frozenset(
    {
        "line_number",
        "candidate_material_description",
        "canonical_display_name",
        "size_description",
        "specification",
        "material_id",
        "full_colly_count",
        "qty_per_full_colly",
        "partial_qty",
        "total_qty",
        "unit",
    }
)
_UNITS = frozenset({"sheet", "pcs", "kg", "roll", "pack"})
_INPUT_TYPES = {member.value: member for member in InputType}
_EVENT_FAILURES = {member.value: member for member in EventDeliveryFailureCode}
_PIPELINE_INPUT = {
    InputType.PDF: InputType.DOCUMENT,
    InputType.DOC: InputType.DOCUMENT,
    InputType.SPREADSHEET: InputType.DOCUMENT,
    InputType.WEB_LINK: InputType.TEXT,
    InputType.YOUTUBE_LINK: InputType.TEXT,
}

_CONTROL_EXIT = {
    CandidateCreateControlFailureCode.AUTHORIZATION_DISABLED: 10,
    CandidateCreateControlFailureCode.AUTHORIZATION_EXPIRED: 10,
    CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMED: 20,
    CandidateCreateControlFailureCode.AUTHORIZATION_INVALID: 30,
    CandidateCreateControlFailureCode.AUTHORIZATION_ACTOR_INVALID: 30,
    CandidateCreateControlFailureCode.AUTHORIZATION_BINDING_INVALID: 30,
    CandidateCreateControlFailureCode.AUTHORIZATION_CONSUMPTION_STATE_INVALID: 30,
    CandidateCreateControlFailureCode.AUTHORIZATION_DURABILITY_FAILED: 30,
}
_INPUT_EXIT = {member: 40 for member in CandidateInputFailureCode}
_REVIEW_EXIT = {
    ReviewFailureCode.ACTOR_REQUIRED: 40,
    ReviewFailureCode.ACTOR_INVALID: 40,
    ReviewFailureCode.ACTOR_UNAUTHORIZED: 40,
    ReviewFailureCode.SOURCE_IDENTITY_INVALID: 40,
    ReviewFailureCode.SOURCE_IDENTITY_CONFLICT: 40,
    ReviewFailureCode.INVALID_REVIEW_REQUEST: 40,
    ReviewFailureCode.CANDIDATE_OPERATION_FAILED: 50,
    ReviewFailureCode.INTERNAL_FAILURE: 50,
    ReviewFailureCode.SOURCE_ACTIVE_RECEIPT_EXISTS: 50,
}
_EXIT_CLASS = {
    0: "SUCCESS",
    10: "AUTHORIZATION_OR_ACTIVATION_REJECTED",
    20: "AUTHORIZATION_ALREADY_CONSUMED",
    30: "AUTHORIZATION_STATE_INVALID_OR_UNUSABLE",
    40: "INPUT_OR_BUSINESS_VALIDATION_REJECTED",
    50: "CONTROLLED_APPLICATION_DOMAIN_OR_PERSISTENCE_FAILURE",
    60: "HARNESS_OUTPUT_OR_EVIDENCE_DURABILITY_FAILURE",
    70: "HARNESS_INTERNAL_FAILURE",
}
_EXIT_MESSAGE = {
    0: "controlled candidate creation succeeded",
    10: "authorization or activation rejected",
    20: "authorization already consumed",
    30: "authorization state invalid or unusable",
    40: "input or business validation rejected",
    50: "controlled application failure",
    60: "harness output or evidence durability failure",
    70: "harness internal failure",
}


class _InputRejected(ValueError):
    """Internal marker whose message is never emitted."""


def _reject() -> NoReturn:
    raise _InputRejected


def _duplicates_rejected(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _reject()
        result[key] = value
    return result


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _closed(value: object, fields: frozenset[str]) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        _reject()
    return value


def _canonical_text(value: object, *, optional: bool, maximum: int) -> str | None:
    if optional and value is None:
        return None
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > maximum
        or any(unicodedata.category(character) in {"Cc", "Cs"} for character in value)
    ):
        _reject()
    return value


def _integer(value: object, *, minimum: int, maximum: int) -> int:
    if type(value) is not int or value < minimum or value > maximum:
        _reject()
    return value


def _decimal_value(
    value: object,
    *,
    maximum: Decimal,
    zero_allowed: bool,
) -> Decimal:
    if type(value) is not str:
        _reject()
    try:
        parsed = Decimal(value)
    except Exception:
        _reject()
    if not parsed.is_finite() or parsed < 0 or (not zero_allowed and parsed == 0):
        _reject()
    sign, digits, exponent = parsed.as_tuple()
    scale = max(-exponent, 0)
    precision = len(digits) + max(exponent, 0)
    if scale > 6 or precision > 20 or parsed > maximum:
        _reject()
    rendered = format(parsed, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if parsed == 0:
        rendered = "0"
    if sign and parsed != 0:
        _reject()
    if _DECIMAL.fullmatch(rendered) is None or rendered != value:
        _reject()
    return parsed


def _canonical_uuid(value: object) -> UUID:
    if type(value) is not str or len(value) != 36:
        _reject()
    try:
        parsed = UUID(value)
    except (AttributeError, TypeError, ValueError):
        _reject()
    if str(parsed) != value:
        _reject()
    return parsed


def _canonical_date(value: object) -> date | None:
    if value is None:
        return None
    if type(value) is not str or len(value) != 10:
        _reject()
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _reject()
    if parsed.isoformat() != value:
        _reject()
    return parsed


def _canonical_received_at(value: object) -> datetime:
    if type(value) is not str or len(value) != 27 or not value.endswith("Z"):
        _reject()
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        _reject()
    if parsed.strftime("%Y-%m-%dT%H:%M:%S.%fZ") != value:
        _reject()
    return parsed


def _ingestion(value: object) -> IngestionResult:
    current = _closed(value, _INGESTION_FIELDS)
    input_name = current["input_type"]
    recognized_name = current["recognized_input_type"]
    if type(input_name) is not str or type(recognized_name) is not str:
        _reject()
    try:
        input_type = _INPUT_TYPES[input_name]
        recognized = _INPUT_TYPES[recognized_name]
    except KeyError:
        _reject()
    if input_type is not _PIPELINE_INPUT.get(recognized, recognized):
        _reject()
    manifest = current["manifest_path"]
    if type(manifest) is not str or len(manifest) != 76 or _MANIFEST.fullmatch(manifest) is None:
        _reject()
    _canonical_uuid(manifest[-41:-5])
    if current["stored_path"] is not None or current["metadata"] != {} or current["text"] != "":
        _reject()
    if current["brain_result"] is not None:
        _reject()
    fixed = {
        "register_handoff_ready": True,
        "process_handoff_ready": False,
        "respond_acknowledgement_ready": True,
    }
    if any(current[key] is not expected for key, expected in fixed.items()):
        _reject()
    boolean_names = (
        "route_handoff_ready",
        "registration_succeeded",
        "event_publication_attempted",
        "event_delivery_succeeded",
    )
    if any(type(current[name]) is not bool for name in boolean_names):
        _reject()
    registered = current["registration_succeeded"]
    registry_id = current["registry_record_id"]
    if registered:
        registry_id = _integer(registry_id, minimum=1, maximum=9_223_372_036_854_775_807)
    elif registry_id is not None:
        _reject()
    attempted = current["event_publication_attempted"]
    delivered = current["event_delivery_succeeded"]
    routed = current["route_handoff_ready"]
    failure_name = current["event_delivery_failure_code"]
    if attempted and not registered:
        _reject()
    if delivered and not attempted:
        _reject()
    if routed and not delivered:
        _reject()
    failure: EventDeliveryFailureCode | None
    if attempted and not delivered:
        if type(failure_name) is not str:
            _reject()
        try:
            failure = _EVENT_FAILURES[failure_name]
        except KeyError:
            _reject()
    else:
        if failure_name is not None:
            _reject()
        failure = None
    return IngestionResult(
        input_type=input_type,
        recognized_input_type=recognized,
        stored_path=None,
        manifest_path=manifest,
        metadata={},
        text="",
        register_handoff_ready=True,
        process_handoff_ready=False,
        route_handoff_ready=routed,
        respond_acknowledgement_ready=True,
        registration_succeeded=registered,
        registry_record_id=registry_id,
        event_publication_attempted=attempted,
        event_delivery_succeeded=delivered,
        event_delivery_failure_code=failure,
        brain_result=None,
    )


def _item(value: object) -> TrustedReceiptItemFacts:
    current = _closed(value, _ITEM_FIELDS)
    line = _integer(current["line_number"], minimum=1, maximum=500)
    texts = [
        _canonical_text(current[name], optional=True, maximum=512)
        for name in (
            "candidate_material_description",
            "canonical_display_name",
            "size_description",
            "specification",
        )
    ]
    material = current["material_id"]
    material_id = None if material is None else _canonical_uuid(material)
    count = _integer(current["full_colly_count"], minimum=0, maximum=1_000_000)
    per_value = current["qty_per_full_colly"]
    if count == 0:
        if per_value is not None:
            _reject()
        per_colly = None
        formula_per_colly = Decimal(0)
    else:
        per_colly = _decimal_value(
            per_value, maximum=Decimal("1000000"), zero_allowed=False
        )
        formula_per_colly = per_colly
    partial = _decimal_value(
        current["partial_qty"], maximum=Decimal("1000000000"), zero_allowed=True
    )
    total = _decimal_value(
        current["total_qty"], maximum=Decimal("1000000000"), zero_allowed=False
    )
    unit = current["unit"]
    if type(unit) is not str or unit not in _UNITS:
        _reject()
    if total != Decimal(count) * formula_per_colly + partial:
        _reject()
    quantities = (partial, total) + (() if per_colly is None else (per_colly,))
    if unit == "sheet" and any(number != number.to_integral_value() for number in quantities):
        _reject()
    return TrustedReceiptItemFacts(
        line,
        texts[0],
        texts[1],
        texts[2],
        texts[3],
        material_id,
        count,
        per_colly,
        partial,
        total,
        unit,
    )


def _facts(value: object) -> TrustedReceiptFacts:
    current = _closed(value, _FACT_FIELDS)
    supplier = _canonical_text(current["supplier_name"], optional=False, maximum=128)
    document_number = _canonical_text(
        current["document_number"], optional=True, maximum=128
    )
    raw_items = current["items"]
    if type(raw_items) is not list or not 1 <= len(raw_items) <= 500:
        _reject()
    items = tuple(_item(item) for item in raw_items)
    lines = tuple(item.line_number for item in items)
    if len(lines) != len(set(lines)):
        _reject()
    return TrustedReceiptFacts(
        supplier,
        document_number,
        _canonical_date(current["document_date"]),
        _canonical_received_at(current["received_at"]),
        items,
    )


def _request_from_transport(
    raw: bytes, expected_sha256: str
) -> tuple[ControlledCandidateCreateRequest, str]:
    if type(raw) is not bytes or len(raw) > MAX_TRANSPORT_INPUT_BYTES:
        _reject()
    if _SHA256.fullmatch(expected_sha256) is None:
        _reject()
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        _reject()
    semantic = raw[:-1]
    if len(semantic) > MAX_SEMANTIC_INPUT_BYTES:
        _reject()
    try:
        text = semantic.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_duplicates_rejected,
            parse_constant=lambda _value: _reject(),
        )
    except (_InputRejected, UnicodeError, json.JSONDecodeError, ValueError):
        _reject()
    current = _closed(value, _TOP_FIELDS)
    if current["schema_version"] != _SCHEMA_VERSION:
        _reject()
    try:
        request = ControlledCandidateCreateRequest(
            _ingestion(current["ingestion_result"]),
            _facts(current["trusted_receipt_facts"]),
        )
    except (CandidateInputError, TypeError, ValueError):
        _reject()
    if _canonical_json(current) != semantic:
        _reject()
    digest = hashlib.sha256(semantic).hexdigest()
    if digest != expected_sha256:
        _reject()
    return request, digest


def _harness_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _envelope(
    code: int,
    input_sha256: str,
    *,
    error: str | None,
    result: ReceiptForReview | None = None,
) -> dict[str, object]:
    if result is None:
        receipt_id = status = source = version = confirmed = item_count = None
        outcome = "FAILURE"
    else:
        if (
            type(result) is not ReceiptForReview
            or type(result.receipt_id) is not UUID
            or type(result.status) is not ReceiptStatus
            or type(result.source_asset_reference) is not str
            or type(result.version) is not int
            or result.version < 0
            or (
                result.confirmed_version is not None
                and type(result.confirmed_version) is not int
            )
            or type(result.items) is not tuple
            or not 1 <= len(result.items) <= 500
        ):
            raise TypeError
        receipt_id = str(result.receipt_id)
        status = result.status.value
        source = result.source_asset_reference
        version = result.version
        confirmed = result.confirmed_version
        item_count = len(result.items)
        outcome = "SUCCESS"
    return {
        "schema_version": _RESULT_SCHEMA_VERSION,
        "outcome": outcome,
        "receipt_id": receipt_id,
        "status": status,
        "source_manifest_reference": source,
        "version": version,
        "confirmed_version": confirmed,
        "item_count": item_count,
        "input_sha256": input_sha256,
        "harness_sha256": _harness_sha256(),
        "exit_classification": _EXIT_CLASS[code],
        "exit_code": code,
        "error_classification": error,
        "message": _EXIT_MESSAGE[code],
    }


def _valid_result(result: object) -> bool:
    try:
        source = result.source_asset_reference
        return (
            type(result) is ReceiptForReview
            and type(result.receipt_id) is UUID
            and result.status is ReceiptStatus.NEEDS_REVIEW
            and type(source) is str
            and len(source) == 76
            and _MANIFEST.fullmatch(source) is not None
            and str(UUID(source[-41:-5])) == source[-41:-5]
            and type(result.version) is int
            and result.version >= 0
            and result.confirmed_version is None
            and result.confirmed_at is None
            and result.confirmation_actor_reference is None
            and type(result.items) is tuple
            and 1 <= len(result.items) <= 500
        )
    except Exception:
        return False


def _fixed_failure_bytes(code: int) -> bytes:
    value = {
        "confirmed_version": None,
        "error_classification": _EXIT_CLASS[code],
        "exit_classification": _EXIT_CLASS[code],
        "exit_code": code,
        "harness_sha256": "0" * 64,
        "input_sha256": "0" * 64,
        "item_count": None,
        "message": _EXIT_MESSAGE[code],
        "outcome": "FAILURE",
        "receipt_id": None,
        "schema_version": _RESULT_SCHEMA_VERSION,
        "source_manifest_reference": None,
        "status": None,
        "version": None,
    }
    return _canonical_json(value) + b"\n"


_SAFE_EXIT_60 = _fixed_failure_bytes(60)
_SAFE_EXIT_70 = _fixed_failure_bytes(70)


def _serialized(
    code: int,
    input_sha256: str,
    *,
    error: str | None,
    result: ReceiptForReview | None = None,
) -> tuple[int, bytes]:
    try:
        payload = _canonical_json(
            _envelope(code, input_sha256, error=error, result=result)
        ) + b"\n"
        if len(payload) > MAX_OUTPUT_BYTES:
            return 60, _SAFE_EXIT_60
        return code, payload
    except Exception:
        return 60, _SAFE_EXIT_60


def _known_failure(exc: BaseException) -> tuple[int, str] | None:
    try:
        if (
            type(exc) is CandidateCreateControlError
            and type(exc.code) is CandidateCreateControlFailureCode
        ):
            return _CONTROL_EXIT[exc.code], exc.code.value
        if type(exc) is CandidateInputError and type(exc.code) is CandidateInputFailureCode:
            return _INPUT_EXIT[exc.code], exc.code.value
        if type(exc) is ReviewApplicationError and type(exc.code) is ReviewFailureCode:
            return _REVIEW_EXIT[exc.code], exc.code.value
    except Exception:
        return None
    return None


async def _execute_transport(raw: bytes, expected_sha256: str) -> tuple[int, bytes]:
    try:
        request, input_sha256 = _request_from_transport(raw, expected_sha256)
    except Exception as exc:
        if type(exc) is _InputRejected:
            return _serialized(
                40,
                "0" * 64,
                error="HARNESS_INPUT_VALIDATION_REJECTED",
            )
        return 70, _SAFE_EXIT_70

    global _state
    with _claim_lock:
        if _state != _UNUSED:
            return _serialized(70, input_sha256, error="HARNESS_INTERNAL_FAILURE")
        _state = _CLAIMED
    try:
        result = await controlled_create_review_candidate(request)
    except asyncio.CancelledError:
        return _serialized(70, input_sha256, error="HARNESS_INTERNAL_FAILURE")
    except Exception as exc:
        known = _known_failure(exc)
        if known is None:
            return _serialized(70, input_sha256, error="HARNESS_INTERNAL_FAILURE")
        code, classification = known
        return _serialized(code, input_sha256, error=classification)
    if not _valid_result(result):
        return _serialized(70, input_sha256, error="HARNESS_INTERNAL_FAILURE")
    return _serialized(0, input_sha256, error=None, result=result)


def _bounded_regular_bytes(path: str) -> bytes:
    candidate = Path(path)
    descriptor: int | None = None
    try:
        metadata = os.stat(candidate, follow_symlinks=False)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_TRANSPORT_INPUT_BYTES:
            _reject()
        descriptor = os.open(
            candidate,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
            _reject()
        chunks: list[bytes] = []
        remaining = MAX_TRANSPORT_INPUT_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > MAX_TRANSPORT_INPUT_BYTES:
            _reject()
        return raw
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _arguments(argv: list[str]) -> tuple[str, str]:
    if len(argv) != 4 or argv[0] != "--input-envelope" or argv[2] != "--expected-input-sha256":
        _reject()
    if not os.path.isabs(argv[1]) or _SHA256.fullmatch(argv[3]) is None:
        _reject()
    return argv[1], argv[3]


def _write_stdout(payload: bytes) -> None:
    written = sys.stdout.buffer.write(payload)
    if written != len(payload):
        raise OSError
    sys.stdout.buffer.flush()


def _catastrophic() -> int:
    try:
        sys.stderr.buffer.write(CATASTROPHIC_STDERR)
        sys.stderr.buffer.flush()
    except Exception:
        pass
    return 70


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        path, expected = _arguments(arguments)
        raw = _bounded_regular_bytes(path)
    except Exception as exc:
        if type(exc) is _InputRejected or isinstance(exc, OSError):
            code, payload = _serialized(
                40, "0" * 64, error="HARNESS_INPUT_VALIDATION_REJECTED"
            )
        else:
            code, payload = 70, _SAFE_EXIT_70
    else:
        try:
            code, payload = asyncio.run(_execute_transport(raw, expected))
        except asyncio.CancelledError:
            code, payload = 70, _SAFE_EXIT_70
        except Exception:
            code, payload = 70, _SAFE_EXIT_70
    try:
        _write_stdout(payload)
    except Exception:
        return _catastrophic()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
