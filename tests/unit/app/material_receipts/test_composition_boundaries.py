from __future__ import annotations

import ast
import importlib
import inspect
import os
from pathlib import Path

import psycopg

from core.app.material_receipts import composition
from core.app.material_receipts.review_use_cases import ReviewFacade
from core.material_receipts.repository import CandidateDatabaseConfig


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


def test_composition_constructs_only_inert_candidate_repository(monkeypatch) -> None:
    connection_calls = 0

    async def reject_connection(*args, **kwargs):
        nonlocal connection_calls
        connection_calls += 1
        raise AssertionError("composition must not connect")

    monkeypatch.setattr(psycopg.AsyncConnection, "connect", reject_connection)
    graph = composition.compose_review_application(
        CandidateDatabaseConfig(password="candidate-test-only")
    )

    assert isinstance(graph.facade, ReviewFacade)
    assert connection_calls == 0


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


def test_environment_composition_loads_only_candidate_password(monkeypatch) -> None:
    requested: list[str] = []

    def governed_get(name: str, default=None):
        requested.append(name)
        if name == "AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD":
            return "candidate-test-only"
        return default

    monkeypatch.setattr(os.environ, "get", governed_get)
    graph = composition.compose_review_application_from_environment()

    assert isinstance(graph.facade, ReviewFacade)
    assert requested == ["AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD"]
    assert all("POSTING" not in name for name in requested)


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
    assert [field.name for field in fields_for(composition.ReviewComposition)] == [
        "facade"
    ]
    graph = composition.compose_review_application(
        CandidateDatabaseConfig(password="candidate-test-only")
    )
    assert not hasattr(graph, "repository")
    assert not hasattr(graph.facade, "repository")
    assert not hasattr(graph.facade, "get_repository")


def fields_for(cls: type):
    return cls.__dataclass_fields__.values()


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
        assert all(not any(word in name.lower() for word in prohibited) for name in parameters)
