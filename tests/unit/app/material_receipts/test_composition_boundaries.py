from __future__ import annotations

import ast
import asyncio
from dataclasses import fields, is_dataclass
import importlib
import inspect
import os
from pathlib import Path
from stat import S_IFLNK, S_IFREG
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest

from core.app.material_receipts import composition
from core.app.material_receipts.results import (
    ReviewApplicationError,
    ReviewFailureCode,
)
from core.app.material_receipts.review_use_cases import (
    ReviewFacade,
    SourceContext,
)
from core.material_receipts.repository import (
    CandidateDatabaseConfig,
    MaterialReceiptRepository,
)


from tests.unit.app.material_receipts.test_review_use_cases import candidate_request

ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = ROOT / "core/app/material_receipts"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def reachable_objects(root: object) -> tuple[object, ...]:
    pending = [root]
    seen: dict[int, object] = {}
    while pending:
        value = pending.pop()
        if id(value) in seen:
            continue
        seen[id(value)] = value
        if is_dataclass(value) and not isinstance(value, type):
            pending.extend(getattr(value, field.name) for field in fields(value))
        values = getattr(value, "__dict__", None)
        if isinstance(values, dict):
            pending.extend(values.values())
        for slot in getattr(type(value), "__slots__", ()):
            attribute = slot
            if slot.startswith("__") and not slot.endswith("__"):
                attribute = f"_{type(value).__name__}{slot}"
            if hasattr(value, attribute):
                pending.append(getattr(value, attribute))
        if inspect.ismethod(value):
            pending.append(value.__self__)
        if inspect.isfunction(value) and value.__closure__:
            pending.extend(cell.cell_contents for cell in value.__closure__)
    return tuple(seen.values())


def test_composition_is_inert_and_environment_independent(monkeypatch) -> None:
    connection_calls = 0
    environment_reads: list[str] = []

    async def reject_connection(*args, **kwargs):
        nonlocal connection_calls
        connection_calls += 1
        raise AssertionError("composition must not connect")

    def record_get(name: str, default=None):
        environment_reads.append(name)
        return default

    monkeypatch.setattr(psycopg.AsyncConnection, "connect", reject_connection)
    monkeypatch.setattr(os.environ, "get", record_get)
    graph = composition.compose_review_application()

    assert isinstance(graph.facade, ReviewFacade)
    assert connection_calls == 0
    assert environment_reads == []


def test_import_and_reload_have_no_connection_or_environment_side_effect(monkeypatch) -> None:
    connection_calls = 0
    before = dict(os.environ)

    async def reject_connection(*args, **kwargs):
        nonlocal connection_calls
        connection_calls += 1
        raise AssertionError("import must not connect")

    monkeypatch.setattr(psycopg.AsyncConnection, "connect", reject_connection)
    importlib.reload(composition)

    assert connection_calls == 0
    assert dict(os.environ) == before


def test_filesystem_verifier_accepts_only_retained_regular_manifest(monkeypatch) -> None:
    reference = (
        "/opt/aios/data/documents/manifests/"
        f"{uuid4()}.json"
    )
    context = SourceContext(reference)
    verifier = composition._FilesystemRetainedEvidenceVerifier()
    calls: list[tuple[str, bool]] = []

    def regular(path: str, *, follow_symlinks: bool):
        calls.append((path, follow_symlinks))
        return SimpleNamespace(st_mode=S_IFREG)

    monkeypatch.setattr(composition.os, "stat", regular)
    assert verifier.is_retained(context) is True
    assert calls == [(reference, False)]

    monkeypatch.setattr(
        composition.os,
        "stat",
        lambda *args, **kwargs: SimpleNamespace(st_mode=S_IFLNK),
    )
    assert verifier.is_retained(context) is False

    def missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(composition.os, "stat", missing)
    assert verifier.is_retained(context) is False



def test_returned_graph_retains_only_narrow_stateless_capabilities() -> None:
    graph = composition.compose_review_application()
    reachable = reachable_objects(graph)

    assert not any(isinstance(value, MaterialReceiptRepository) for value in reachable)
    assert not any(isinstance(value, CandidateDatabaseConfig) for value in reachable)
    assert not any(
        isinstance(value, str)
        and ("postgresql://" in value or "password=" in value)
        for value in reachable
    )
    forbidden = (
        "confirm_receipt",
        "reject_receipt",
        "cancel_receipt",
        "cancel_receipt_item",
        "post_confirmed_receipt",
        "get_repository",
        "execute",
        "_call",
    )
    for value in reachable:
        for name in forbidden:
            assert not hasattr(value, name)


def test_traversed_candidate_capability_cannot_bypass_retention(monkeypatch) -> None:
    request = candidate_request()

    def missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(composition.os, "stat", missing)
    graph = composition.compose_review_application()
    port = graph.facade._ReviewFacade__candidate_port

    with pytest.raises(ReviewApplicationError) as caught:
        asyncio.run(port.create_candidate(request))

    assert caught.value.code is ReviewFailureCode.SOURCE_IDENTITY_INVALID



def test_review_package_has_no_posting_brain_telegram_or_ingestion_imports() -> None:
    imports = set()
    for path in PACKAGE_ROOT.glob("*.py"):
        imports.update(imported_modules(path))
    prohibited = (
        "core.inventory_posting",
        "core.brain",
        "core.adapters.telegram",
        "core.ingestion",
        "core.registry",
    )
    assert not {name for name in imports if name.startswith(prohibited)}


def test_posting_repository_construction_and_capability_count_is_zero() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in PACKAGE_ROOT.glob("*.py")
    )
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "InventoryPostingRepository" not in calls
    assert "PostingDatabaseConfig" not in calls
    assert "post_confirmed_receipt" not in source
    assert "confirm_receipt" not in source
    assert "AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD" not in source


def test_composition_public_graph_exposes_only_facade() -> None:
    assert [field.name for field in fields(composition.ReviewComposition)] == [
        "facade"
    ]
    graph = composition.compose_review_application()
    assert not hasattr(graph, "repository")
    assert not hasattr(graph.facade, "repository")
    assert not hasattr(graph.facade, "get_repository")
    assert not hasattr(graph.facade, "_call")


def test_no_generic_execution_or_authority_parameters_enter_use_cases() -> None:
    prohibited = {
        "sql", "dsn", "connection", "environment", "repository", "credential",
        "password", "token", "execute", "brain", "telegram", "confirm", "post",
    }
    for operation in (
        ReviewFacade.create_candidate,
        ReviewFacade.revise_candidate,
        ReviewFacade.get_candidate_for_review,
    ):
        parameters = inspect.signature(operation).parameters
        assert all(
            not any(word in name.lower() for word in prohibited)
            for name in parameters
        )
