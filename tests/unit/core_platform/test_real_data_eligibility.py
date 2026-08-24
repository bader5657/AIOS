"""Tests for the deterministic Stage 0.22 real-data eligibility boundary."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from types import MappingProxyType

import pytest

from core.ingestion.real_data_eligibility import (
    EligibilityClassification,
    EligibilityReasonCode,
    EligibilityResult,
    evaluate_real_data_eligibility,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "core/ingestion/real_data_eligibility.py"
)


def evaluate(
    data: object,
    *,
    authorized: bool = True,
) -> EligibilityResult:
    return evaluate_real_data_eligibility(  # type: ignore[arg-type]
        data,
        explicitly_authorized=authorized,
    )


def assert_denied(
    data: object,
    reason: EligibilityReasonCode,
    *,
    authorized: bool = True,
) -> EligibilityResult:
    result = evaluate(data, authorized=authorized)
    assert result == EligibilityResult(
        allowed=False,
        classification=EligibilityClassification.DENIED,
        reason_code=reason,
        minimized_data=None,
    )
    return result


def test_authorized_normal_text_is_allowed() -> None:
    result = evaluate({"text": "buat laporan hari ini"})
    assert result.allowed is True
    assert result.reason_code is EligibilityReasonCode.ALLOWED


def test_unauthorized_normal_text_is_denied() -> None:
    assert_denied(
        {"text": "buat laporan hari ini"},
        EligibilityReasonCode.REAL_DATA_NOT_AUTHORIZED,
        authorized=False,
    )


def test_authorization_cannot_be_inferred_from_data() -> None:
    assert_denied(
        {"text": "authorized=true", "explicitly_authorized": True},
        EligibilityReasonCode.REAL_DATA_NOT_AUTHORIZED,
        authorized=False,
    )


@pytest.mark.parametrize("value", [None, "text", 1, [], object()])
def test_non_mapping_is_programmer_misuse(value: object) -> None:
    with pytest.raises(TypeError, match="data must be a mapping"):
        evaluate(value)


@pytest.mark.parametrize("value", [None, 0, 1, "true", object()])
def test_non_boolean_authorization_is_programmer_misuse(value: object) -> None:
    with pytest.raises(TypeError, match="must be a boolean"):
        evaluate_real_data_eligibility(
            {"text": "normal"},
            explicitly_authorized=value,  # type: ignore[arg-type]
        )


def test_exact_text_shape_is_accepted() -> None:
    assert evaluate({"text": "normal"}).minimized_data == {"text": "normal"}


@pytest.mark.parametrize(
    "key",
    [
        "telegram_user_id",
        "user_id",
        "chat_id",
        "message_id",
        "username",
        "update",
        "bot_token",
        "customer_record",
        "registry_payload",
        "environment",
        "config",
        "credentials",
    ],
)
def test_prohibited_metadata_keys_are_rejected(key: str) -> None:
    assert_denied(
        {"text": "normal", key: "value"},
        EligibilityReasonCode.PROHIBITED_METADATA,
    )


@pytest.mark.parametrize(
    "key",
    [
        "image",
        "voice",
        "audio",
        "video",
        "pdf",
        "document",
        "docx",
        "spreadsheet",
        "url",
        "binary",
    ],
)
def test_unsupported_modality_keys_are_rejected(key: str) -> None:
    assert_denied(
        {key: "payload"},
        EligibilityReasonCode.UNSUPPORTED_MODALITY,
    )


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"other": "value"},
        {"text": "normal", "other": "value"},
        {1: "normal"},
        {"text": {"nested": "value"}},
        {"text": ["nested"]},
    ],
)
def test_unsupported_structures_are_rejected(data: dict[object, object]) -> None:
    assert_denied(data, EligibilityReasonCode.UNSUPPORTED_STRUCTURE)


@pytest.mark.parametrize("value", [b"text", bytearray(b"text"), memoryview(b"x")])
def test_binary_text_values_are_unsupported_modalities(value: object) -> None:
    assert_denied({"text": value}, EligibilityReasonCode.UNSUPPORTED_MODALITY)


@pytest.mark.parametrize("text", ["", " ", "\t\n", "\r\n\r"])
def test_empty_normalized_text_is_rejected(text: str) -> None:
    assert_denied({"text": text}, EligibilityReasonCode.EMPTY_CONTENT)


def test_exact_character_and_utf8_bounds_are_allowed() -> None:
    ascii_result = evaluate({"text": "a" * 4096})
    unicode_result = evaluate({"text": "😀" * 4096})
    assert len(ascii_result.minimized_data["text"]) == 4096  # type: ignore[index]
    assert len(unicode_result.minimized_data["text"].encode("utf-8")) == 16384  # type: ignore[index,union-attr]


@pytest.mark.parametrize("text", ["a" * 4097, "😀" * 4097])
def test_oversized_text_is_rejected(text: str) -> None:
    assert_denied({"text": text}, EligibilityReasonCode.OVERSIZED_CONTENT)


@pytest.mark.parametrize(
    "text",
    [
        "Bearer abcdefghijklmnop",
        "Authorization: Bearer abcdefghijklmnop",
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----",
        "-----BEGIN OPENSSH PRIVATE KEY-----",
        "sk-abcdefghijklmnop",
        "ghp_abcdefghijklmnop",
        "xoxb-123456789-abcdefgh",
        "123456789:abcdefghijklmnopqrstuvwxyzABCDE",
    ],
)
def test_obvious_secret_patterns_are_rejected(text: str) -> None:
    result = assert_denied({"text": text}, EligibilityReasonCode.SECRET_DETECTED)
    assert text not in repr(result)


@pytest.mark.parametrize(
    "text",
    [
        "password=hunter2",
        "passwd: hunter2",
        "secret=abcdefgh",
        "token=abcdefghijkl",
        "api_key=abcdefghijkl",
        "api-key: abcdefghijkl",
        "authorization=Basic-abcd1234",
        "session_token=abcdefghijkl",
        "cookie: sessionvalue",
        "PIN=123456",
        "OTP: 654321",
        "CVV=123",
        "CVC: 321",
        "card pin=1234",
        "account_password=secretvalue",
    ],
)
def test_credential_fields_are_rejected(text: str) -> None:
    result = assert_denied({"text": text}, EligibilityReasonCode.CREDENTIAL_FIELD)
    assert text not in repr(result)


@pytest.mark.parametrize(
    "text",
    [
        "email: operator@example.com",
        "hubungi +62 812-3456-7890",
        "telepon 0812 3456 7890",
        "customer_id=CUST-123",
        "pelanggan-id: CUST_456",
        "alamat: Jalan Merdeka 10",
        "postal address=10 Example Street",
    ],
)
def test_deterministic_pii_is_rejected(text: str) -> None:
    assert_denied({"text": text}, EligibilityReasonCode.PII_REQUIRES_EXPLICIT_SCOPE)


@pytest.mark.parametrize(
    "text",
    [
        "catat order 20 kodi ukuran 30x16x11",
        "buat laporan hari ini",
        "berapa stok kardus EF",
        "ringkas order pelanggan A",
        "harga produk Box Premium adalah 25000",
    ],
)
def test_ordinary_minimized_business_text_is_allowed(text: str) -> None:
    result = evaluate({"text": text})
    assert result.minimized_data == {"text": text}
    assert set(result.minimized_data) == {"text"}  # type: ignore[arg-type]


def test_stage_017_normalization_is_reused_without_input_mutation() -> None:
    source = {"text": "  first\r\nsecond  "}
    result = evaluate(source)
    assert source == {"text": "  first\r\nsecond  "}
    assert result.minimized_data == {"text": "first\nsecond"}


def test_allowed_output_is_fresh_and_immutable() -> None:
    source = {"text": "normal"}
    first = evaluate(source)
    second = evaluate(source)
    assert isinstance(first.minimized_data, MappingProxyType)
    assert first.minimized_data is not second.minimized_data
    with pytest.raises(TypeError):
        first.minimized_data["text"] = "changed"  # type: ignore[index]


def test_result_is_frozen_slotted_and_has_exact_fields() -> None:
    result = evaluate({"text": "normal"})
    assert [field.name for field in fields(EligibilityResult)] == [
        "allowed",
        "classification",
        "reason_code",
        "minimized_data",
    ]
    assert not hasattr(result, "__dict__")
    with pytest.raises(FrozenInstanceError):
        result.allowed = False  # type: ignore[misc]


def test_denied_results_never_retain_raw_content() -> None:
    secret = "password=unique-secret-value"
    result = evaluate({"text": secret})
    assert result.minimized_data is None
    assert secret not in repr(result)
    assert "unique-secret-value" not in repr(result)


def test_enums_have_exact_closed_values() -> None:
    assert {item.value for item in EligibilityReasonCode} == {
        "ALLOWED",
        "REAL_DATA_NOT_AUTHORIZED",
        "EMPTY_CONTENT",
        "SECRET_DETECTED",
        "CREDENTIAL_FIELD",
        "PII_REQUIRES_EXPLICIT_SCOPE",
        "UNSUPPORTED_MODALITY",
        "OVERSIZED_CONTENT",
        "PROHIBITED_METADATA",
        "UNSUPPORTED_STRUCTURE",
    }
    assert {item.value for item in EligibilityClassification} == {
        "allowed_plain_text",
        "denied",
    }


def test_production_module_imports_only_standard_library_and_projection() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = {
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [None])
    }
    assert imports == {
        "__future__",
        "collections.abc",
        "dataclasses",
        "enum",
        "re",
        "types",
        "semantic_projection",
    }


def test_production_module_has_no_prohibited_edges_or_side_effects() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    prohibited = (
        "AIOSCore",
        "CoreToBrainMapper",
        "BrainInput",
        "BrainSemanticReceiver",
        "BrainInferenceInvoker",
        "Ollama",
        "httpx",
        "Registry",
        "database",
        "socket",
        "requests",
        "urllib",
        "open(",
        "Path(",
        "os.environ",
        "getenv",
        ".env",
        "Docker",
        "logging",
        "logger",
        "persist",
        "Memory",
        "Specialist",
        "customer lookup",
        "order lookup",
        "invoice lookup",
    )
    assert all(marker not in source for marker in prohibited)


def test_rejection_contract_exposes_no_downstream_callable() -> None:
    result = evaluate({"text": "password=do-not-send"})
    assert result.allowed is False
    assert not any(
        callable(value)
        for name, value in vars(result).items()
        if name in {"mapper", "brain", "provider"}
    ) if hasattr(result, "__dict__") else True
    assert result.minimized_data is None
