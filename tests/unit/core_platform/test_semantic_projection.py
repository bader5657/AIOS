"""Tests for the pure Stage 0.17 runtime semantic text projection."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from core.ingestion.semantic_projection import (
    MAX_SEMANTIC_TEXT_CHARACTERS,
    MAX_SEMANTIC_TEXT_UTF8_BYTES,
    project_text_semantics,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[3] / "core/ingestion/semantic_projection.py"
)


def test_public_function_accepts_text_and_returns_exact_fresh_dict() -> None:
    first = project_text_semantics("  Halo dunia  ")
    second = project_text_semantics("  Halo dunia  ")

    assert first == {"text": "Halo dunia"}
    assert type(first) is dict
    assert set(first) == {"text"}
    assert first is not second
    assert first == second


@pytest.mark.parametrize(
    "value",
    [None, b"text", 1, [], {}, object()],
)
def test_non_string_values_are_rejected_without_coercion(value: object) -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        project_text_semantics(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    ["", "   ", "\t\n\t", "\r\n\r"],
)
def test_empty_normalized_content_is_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="empty after normalization"):
        project_text_semantics(value)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("first\r\nsecond", "first\nsecond"),
        ("first\rsecond", "first\nsecond"),
        ("first\r\nsecond\rthird\nfourth", "first\nsecond\nthird\nfourth"),
    ],
)
def test_line_endings_are_normalized_deterministically(
    source: str,
    expected: str,
) -> None:
    result = project_text_semantics(source)
    assert result == {"text": expected}
    assert "\r" not in result["text"]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("  leading", "leading"),
        ("trailing  ", "trailing"),
        (" \t both \n", "both"),
        ("one two", "one two"),
        ("one  two", "one  two"),
        ("one\ttwo", "one\ttwo"),
        ("one\ntwo", "one\ntwo"),
    ],
)
def test_outer_whitespace_is_trimmed_and_internal_whitespace_is_preserved(
    source: str,
    expected: str,
) -> None:
    assert project_text_semantics(source) == {"text": expected}


def test_character_bound_is_inclusive_without_truncation() -> None:
    accepted = "a" * MAX_SEMANTIC_TEXT_CHARACTERS
    assert project_text_semantics(accepted) == {"text": accepted}

    oversized = accepted + "a"
    with pytest.raises(ValueError, match="Unicode code points"):
        project_text_semantics(oversized)


def test_four_byte_unicode_reaches_exact_combined_bounds() -> None:
    accepted = "😀" * MAX_SEMANTIC_TEXT_CHARACTERS
    assert len(accepted) == MAX_SEMANTIC_TEXT_CHARACTERS
    assert len(accepted.encode("utf-8")) == MAX_SEMANTIC_TEXT_UTF8_BYTES
    assert project_text_semantics(accepted) == {"text": accepted}


def test_utf8_bound_is_an_explicit_defense_in_depth_check() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MODULE_PATH))
    comparisons = [node for node in ast.walk(tree) if isinstance(node, ast.Compare)]

    assert any(
        "len(normalized_text.encode('utf-8'))"
        in ast.unparse(comparison).replace('"', "'")
        and "MAX_SEMANTIC_TEXT_UTF8_BYTES" in ast.unparse(comparison)
        for comparison in comparisons
    )
    # UTF-8 uses at most four bytes per Unicode code point. Consequently,
    # exceeding 16,384 bytes while remaining within 4,096 code points is
    # mathematically impossible; the exact joint boundary is tested above.


@pytest.mark.parametrize("allowed", ["left\tright", "left\nright"])
def test_tab_and_lf_are_allowed(allowed: str) -> None:
    assert project_text_semantics(allowed) == {"text": allowed}


@pytest.mark.parametrize(
    "control",
    ["\x00", "\x01", "\x07", "\x0b", "\x0c", "\x1b", "\x1f", "\x7f"],
)
def test_forbidden_controls_are_rejected_without_silent_removal(
    control: str,
) -> None:
    source = f"before{control}after"
    with pytest.raises(ValueError, match="forbidden ASCII control"):
        project_text_semantics(source)


@pytest.mark.parametrize(
    "text",
    [
        "Bahasa Indonesia tetap sama",
        "مرحبا بالعالم",
        "こんにちは世界",
        "Halo 😀🌏",
        "e\u0301",
        "é",
    ],
)
def test_unicode_code_points_are_preserved_without_normalization(text: str) -> None:
    assert project_text_semantics(text) == {"text": text}


def test_canonically_equivalent_sequences_are_not_rewritten() -> None:
    decomposed = "e\u0301"
    composed = "é"
    assert decomposed != composed
    assert project_text_semantics(decomposed)["text"] == decomposed
    assert project_text_semantics(composed)["text"] == composed


def test_module_is_standard_library_only_and_has_no_runtime_side_effect_edges() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MODULE_PATH))

    assert not [
        node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    prohibited = (
        "telegram",
        "RequestContext",
        "InputType",
        "EventEnvelope",
        "CoreToBrainMapper",
        "BrainInput",
        "BrainSemanticReceiver",
        "BrainInferenceInvoker",
        "provider",
        "Ollama",
        "Registry",
        "database",
        "filesystem",
        "network",
        "environ",
        "getenv",
        "config",
        "logging",
        "logger",
        "persist",
        "Memory",
        "Specialist",
        "core.domain",
        "correlation_id",
        "input_reference",
        "context_references",
        "customer",
        "invoice",
        "transaction",
        "secret",
        "token",
    )
    for marker in prohibited:
        assert marker not in source


def test_function_has_one_required_parameter_and_no_configuration() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "project_text_semantics"
    ]
    assert len(functions) == 1
    function = functions[0]
    assert [argument.arg for argument in function.args.args] == ["text"]
    assert function.args.defaults == []
    assert function.args.kwonlyargs == []
    assert function.args.vararg is None
    assert function.args.kwarg is None
