"""Deterministic real-data eligibility boundary for minimized plain text."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import re
from types import MappingProxyType

from .semantic_projection import project_text_semantics


class EligibilityClassification(str, Enum):
    """Provider-neutral classification of one eligibility decision."""

    ALLOWED_PLAIN_TEXT = "allowed_plain_text"
    DENIED = "denied"


class EligibilityReasonCode(str, Enum):
    """Closed vocabulary for real-data eligibility outcomes."""

    ALLOWED = "ALLOWED"
    REAL_DATA_NOT_AUTHORIZED = "REAL_DATA_NOT_AUTHORIZED"
    EMPTY_CONTENT = "EMPTY_CONTENT"
    SECRET_DETECTED = "SECRET_DETECTED"
    CREDENTIAL_FIELD = "CREDENTIAL_FIELD"
    PII_REQUIRES_EXPLICIT_SCOPE = "PII_REQUIRES_EXPLICIT_SCOPE"
    UNSUPPORTED_MODALITY = "UNSUPPORTED_MODALITY"
    OVERSIZED_CONTENT = "OVERSIZED_CONTENT"
    PROHIBITED_METADATA = "PROHIBITED_METADATA"
    UNSUPPORTED_STRUCTURE = "UNSUPPORTED_STRUCTURE"


@dataclass(frozen=True, slots=True)
class EligibilityResult:
    """Immutable decision that never retains rejected semantic content."""

    allowed: bool
    classification: EligibilityClassification
    reason_code: EligibilityReasonCode
    minimized_data: Mapping[str, object] | None


_PROHIBITED_METADATA_KEYS = frozenset(
    {
        "bot_token",
        "chat_id",
        "config",
        "credentials",
        "customer_record",
        "environment",
        "message_id",
        "registry_payload",
        "session_state",
        "telegram_user_id",
        "update",
        "update_state",
        "user_id",
        "username",
    }
)
_UNSUPPORTED_MODALITY_KEYS = frozenset(
    {
        "audio",
        "binary",
        "doc",
        "document",
        "docx",
        "file",
        "image",
        "pdf",
        "spreadsheet",
        "url",
        "video",
        "voice",
    }
)

_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN\s+(?:(?:RSA|OPENSSH|EC|DSA)\s+)?PRIVATE\s+KEY-----",
    re.IGNORECASE,
)
_BEARER_PATTERN = re.compile(
    r"\b(?:authorization\s*:\s*)?bearer\s+[A-Za-z0-9._~+/=-]{8,}",
    re.IGNORECASE,
)
_KNOWN_TOKEN_PATTERN = re.compile(
    r"(?:\bsk-[A-Za-z0-9_-]{8,}|\bgh[pousr]_[A-Za-z0-9]{8,}|"
    r"\bxox[baprs]-[A-Za-z0-9-]{8,}|\bAIza[0-9A-Za-z_-]{16,}|"
    r"\b\d{6,12}:[A-Za-z0-9_-]{20,}\b)"
)
_CREDENTIAL_ASSIGNMENT_PATTERN = re.compile(
    r"\b(?:password|passwd|secret|token|api[_-]?key|authorization|cookie|"
    r"session(?:_?id|_?token)?)\s*[:=]\s*\S+",
    re.IGNORECASE,
)
_FINANCIAL_CREDENTIAL_PATTERN = re.compile(
    r"\b(?:pin|otp|cvv|cvc|card[_ -]?(?:password|pin)|"
    r"account[_ -]?(?:password|pin))\s*[:=]\s*\S+",
    re.IGNORECASE,
)
_EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])",
    re.IGNORECASE,
)
_PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:(?:\+|00)\d(?:[\s().-]*\d){7,14}|"
    r"08\d(?:[\s.-]*\d){7,10})(?!\w)"
)
_CUSTOMER_IDENTIFIER_PATTERN = re.compile(
    r"\b(?:customer|pelanggan)[_ -]?(?:id|identifier)\s*[:=#]\s*"
    r"[A-Za-z0-9][A-Za-z0-9_-]{2,}",
    re.IGNORECASE,
)
_POSTAL_ADDRESS_PATTERN = re.compile(
    r"\b(?:alamat|address|postal[_ -]?address)\s*[:=]\s*\S+",
    re.IGNORECASE,
)


def _denied(reason_code: EligibilityReasonCode) -> EligibilityResult:
    return EligibilityResult(
        allowed=False,
        classification=EligibilityClassification.DENIED,
        reason_code=reason_code,
        minimized_data=None,
    )


def evaluate_real_data_eligibility(
    data: Mapping[str, object],
    *,
    explicitly_authorized: bool,
) -> EligibilityResult:
    """Evaluate one already-minimized real-text candidate without side effects."""
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping")
    if type(explicitly_authorized) is not bool:
        raise TypeError("explicitly_authorized must be a boolean")
    if explicitly_authorized is not True:
        return _denied(EligibilityReasonCode.REAL_DATA_NOT_AUTHORIZED)

    keys = frozenset(data.keys())
    if not all(isinstance(key, str) for key in keys):
        return _denied(EligibilityReasonCode.UNSUPPORTED_STRUCTURE)
    normalized_keys = frozenset(key.casefold() for key in keys)
    if normalized_keys & _PROHIBITED_METADATA_KEYS:
        return _denied(EligibilityReasonCode.PROHIBITED_METADATA)
    if normalized_keys & _UNSUPPORTED_MODALITY_KEYS:
        return _denied(EligibilityReasonCode.UNSUPPORTED_MODALITY)
    if keys != {"text"}:
        return _denied(EligibilityReasonCode.UNSUPPORTED_STRUCTURE)

    text = data["text"]
    if not isinstance(text, str):
        if isinstance(text, (bytes, bytearray, memoryview)):
            return _denied(EligibilityReasonCode.UNSUPPORTED_MODALITY)
        return _denied(EligibilityReasonCode.UNSUPPORTED_STRUCTURE)

    try:
        projected = project_text_semantics(text)
    except ValueError as error:
        message = str(error)
        if "empty after normalization" in message:
            return _denied(EligibilityReasonCode.EMPTY_CONTENT)
        if "exceeds" in message:
            return _denied(EligibilityReasonCode.OVERSIZED_CONTENT)
        return _denied(EligibilityReasonCode.UNSUPPORTED_STRUCTURE)

    allowed_text = projected["text"]
    if not isinstance(allowed_text, str):  # defensive contract containment
        return _denied(EligibilityReasonCode.UNSUPPORTED_STRUCTURE)

    if (
        _PRIVATE_KEY_PATTERN.search(allowed_text)
        or _BEARER_PATTERN.search(allowed_text)
        or _KNOWN_TOKEN_PATTERN.search(allowed_text)
    ):
        return _denied(EligibilityReasonCode.SECRET_DETECTED)
    if (
        _CREDENTIAL_ASSIGNMENT_PATTERN.search(allowed_text)
        or _FINANCIAL_CREDENTIAL_PATTERN.search(allowed_text)
    ):
        return _denied(EligibilityReasonCode.CREDENTIAL_FIELD)
    if (
        _EMAIL_PATTERN.search(allowed_text)
        or _PHONE_PATTERN.search(allowed_text)
        or _CUSTOMER_IDENTIFIER_PATTERN.search(allowed_text)
        or _POSTAL_ADDRESS_PATTERN.search(allowed_text)
    ):
        return _denied(EligibilityReasonCode.PII_REQUIRES_EXPLICIT_SCOPE)

    minimized = MappingProxyType({"text": allowed_text})
    return EligibilityResult(
        allowed=True,
        classification=EligibilityClassification.ALLOWED_PLAIN_TEXT,
        reason_code=EligibilityReasonCode.ALLOWED,
        minimized_data=minimized,
    )
