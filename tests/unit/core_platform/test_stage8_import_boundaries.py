import ast
import sys
import unittest
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CORE_ROOT = REPOSITORY_ROOT / "core"


@dataclass(frozen=True)
class ImportEdge:
    source: str
    source_path: Path
    target: str
    imported_names: tuple[str, ...]


def _module_name(path: Path) -> str:
    relative = path.relative_to(REPOSITORY_ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _resolve_from_module(path: Path, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    source = _module_name(path)
    package = source if path.name == "__init__.py" else source.rpartition(".")[0]
    parts = package.split(".") if package else []
    ascend = node.level - 1
    if ascend:
        parts = parts[:-ascend]
    if node.module:
        parts.extend(node.module.split("."))
    return ".".join(parts)


def _read_imports() -> tuple[dict[str, Path], tuple[ImportEdge, ...]]:
    modules = {}
    edges = []
    for path in sorted(CORE_ROOT.rglob("*.py")):
        source = _module_name(path)
        modules[source] = path
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(
                        ImportEdge(source, path, alias.name, (alias.name,))
                    )
            elif isinstance(node, ast.ImportFrom):
                edges.append(
                    ImportEdge(
                        source,
                        path,
                        _resolve_from_module(path, node),
                        tuple(alias.name for alias in node.names),
                    )
                )
    return modules, tuple(edges)


MODULES, IMPORTS = _read_imports()


def _under(module: str, prefix: str) -> bool:
    return module == prefix or module.startswith(prefix + ".")


def _edges_from(prefix: str) -> tuple[ImportEdge, ...]:
    return tuple(edge for edge in IMPORTS if _under(edge.source, prefix))


def _format_edges(edges) -> str:
    return "\n".join(
        f"{edge.source_path.relative_to(REPOSITORY_ROOT)}: "
        f"{edge.source} -> {edge.target}"
        for edge in edges
    )


def _assert_no_targets(
    testcase: unittest.TestCase,
    source_prefix: str,
    forbidden_prefixes: tuple[str, ...],
) -> None:
    violations = [
        edge
        for edge in _edges_from(source_prefix)
        if any(_under(edge.target, target) for target in forbidden_prefixes)
    ]
    testcase.assertFalse(
        violations,
        f"prohibited imports from {source_prefix}:\n{_format_edges(violations)}",
    )


def _resolved_local_target(target: str) -> str | None:
    candidate = target
    while candidate:
        if candidate in MODULES:
            return candidate
        candidate = candidate.rpartition(".")[0]
    return None


def _module_level_calls(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    calls = []

    def call_name(node: ast.Call) -> str:
        value = node.func
        parts = []
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))

    def is_main_guard(node: ast.If) -> bool:
        try:
            return ast.unparse(node.test) == "__name__ == '__main__'"
        except AttributeError:
            return False

    def inspect_statements(statements) -> None:
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(statement, ast.If):
                if not is_main_guard(statement):
                    inspect_statements(statement.body)
                    inspect_statements(statement.orelse)
                continue
            if isinstance(statement, (ast.Try, ast.With, ast.AsyncWith)):
                inspect_statements(statement.body)
                inspect_statements(getattr(statement, "orelse", ()))
                inspect_statements(getattr(statement, "finalbody", ()))
                continue
            values = []
            if isinstance(statement, ast.Expr):
                values.append(statement.value)
            elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
                values.append(statement.value)
            for value in values:
                for node in ast.walk(value):
                    if isinstance(node, ast.Call):
                        calls.append(call_name(node))

    inspect_statements(tree.body)
    return tuple(calls)


class Stage8ImportBoundaryTests(unittest.TestCase):
    BUSINESS_PREFIXES = (
        "core.domain.customer",
        "core.admin",
        "core.finance",
        "core.content",
        "core.creative",
    )
    LATER_PHASE_PREFIXES = (
        "core.brain",
        "core.memory",
        "core.specialist_router",
        "core.specialists",
    )

    def test_approved_positive_graph_edges_are_present(self):
        expected = {
            ("core.adapters.telegram.main", "core.ingestion.universal_ingestion"),
            ("core.adapters.telegram.main", "core.mission.status"),
            ("core.ingestion.universal_ingestion", "core.app.input_classifier"),
            ("core.ingestion.universal_ingestion", "core.app.request_context"),
            ("core.ingestion.universal_ingestion", "core.pipeline.asset_pipeline"),
            ("core.ingestion.universal_ingestion", "core.registry"),
            ("core.ingestion.universal_ingestion", "core.domain.domain_event"),
            ("core.ingestion.universal_ingestion", "core.domain.event_envelope"),
            ("core.ingestion.universal_ingestion", "core.event"),
            ("core.ingestion.universal_ingestion", "core.aios_core"),
            ("core.ingestion.universal_ingestion", "core.core_to_brain_mapper"),
            ("core.ingestion.universal_ingestion", "core.brain.input_contracts"),
            ("core.ingestion.universal_ingestion", "core.brain.inference_contracts"),
            ("core.pipeline.asset_pipeline", "core.app.request_context"),
            ("core.pipeline.asset_pipeline", "core.storage.telegram_storage"),
            ("core.pipeline.asset_pipeline", "core.storage.metadata_engine"),
            ("core.pipeline.asset_pipeline", "core.storage.document_manifest"),
            ("core.storage.telegram_storage", "core.storage.file_storage"),
            ("core.event.event_engine", "core.domain.event_envelope"),
            ("core.aios_core.core", "core.domain.event_envelope"),
        }
        actual = {(edge.source, edge.target) for edge in IMPORTS}
        self.assertEqual(expected - actual, set())

    def test_storage_registry_event_core_domain_and_pipeline_reverse_edges_are_zero(self):
        _assert_no_targets(
            self,
            "core.storage",
            (
                "core.app", "core.ingestion", "core.registry", "core.event",
                "core.aios_core", *self.LATER_PHASE_PREFIXES, *self.BUSINESS_PREFIXES,
            ),
        )
        _assert_no_targets(
            self,
            "core.registry",
            (
                "core.ingestion", "core.pipeline", "core.storage", "core.event",
                "core.aios_core", *self.LATER_PHASE_PREFIXES, *self.BUSINESS_PREFIXES,
            ),
        )
        _assert_no_targets(
            self,
            "core.event",
            (
                "core.ingestion", "core.registry", "core.aios_core",
                *self.LATER_PHASE_PREFIXES, *self.BUSINESS_PREFIXES,
            ),
        )
        _assert_no_targets(
            self,
            "core.aios_core",
            (
                "core.ingestion", "core.pipeline", "core.storage", "core.registry",
                "core.event", *self.LATER_PHASE_PREFIXES, *self.BUSINESS_PREFIXES,
            ),
        )
        _assert_no_targets(
            self,
            "core.domain",
            (
                "core.adapters", "core.ingestion", "core.pipeline", "core.storage",
                "core.registry", "core.event", "core.aios_core",
                *self.LATER_PHASE_PREFIXES,
            ),
        )
        _assert_no_targets(
            self,
            "core.pipeline",
            (
                "core.registry", "core.event", "core.aios_core",
                *self.LATER_PHASE_PREFIXES, *self.BUSINESS_PREFIXES,
            ),
        )

    def test_adapter_internal_imports_have_only_two_exact_edges(self):
        actual = {
            edge.target
            for edge in _edges_from("core.adapters.telegram")
            if edge.target.startswith("core.")
        }
        self.assertEqual(
            actual,
            {"core.ingestion.universal_ingestion", "core.mission.status"},
        )

    def test_telegram_sdk_exception_is_an_exact_file_set(self):
        actual = {
            edge.source_path.relative_to(REPOSITORY_ROOT).as_posix()
            for edge in IMPORTS
            if _under(edge.target, "telegram")
        }
        self.assertEqual(
            actual,
            {
                "core/adapters/telegram/main.py",
                "core/app/input_classifier.py",
                "core/ingestion/universal_ingestion.py",
                "core/pipeline/asset_pipeline.py",
                "core/storage/telegram_storage.py",
            },
        )

    def test_later_phase_and_business_imports_are_absent_from_stage8_pipeline(self):
        pipeline_roots = (
            "core.adapters.telegram", "core.app.input_classifier",
            "core.app.request_context", "core.ingestion", "core.pipeline",
            "core.storage", "core.registry", "core.event", "core.aios_core",
        )
        allowed_level_a_brain_edges = {
            (
                "core.ingestion.universal_ingestion",
                "core.brain.input_contracts",
                ("BrainInput",),
            ),
            (
                "core.ingestion.universal_ingestion",
                "core.brain.inference_contracts",
                ("InferenceResult",),
            ),
        }
        violations = [
            edge
            for edge in IMPORTS
            if any(_under(edge.source, root) for root in pipeline_roots)
            and any(
                _under(edge.target, target)
                for target in self.LATER_PHASE_PREFIXES + self.BUSINESS_PREFIXES
            )
            and (edge.source, edge.target, edge.imported_names)
            not in allowed_level_a_brain_edges
        ]
        self.assertFalse(violations, _format_edges(violations))

    def test_psycopg_registry_dto_and_result_types_remain_local(self):
        psycopg_sources = {
            edge.source_path.relative_to(REPOSITORY_ROOT).as_posix()
            for edge in IMPORTS
            if _under(edge.target, "psycopg")
        }
        self.assertEqual(
            psycopg_sources,
            {
                "core/registry/postgres_registry.py",
                "core/material_receipts/repository.py",
                "core/inventory_posting/repository.py",
            },
        )

        registry_consumers = {
            edge.source
            for edge in IMPORTS
            if _under(edge.target, "core.registry")
            and not _under(edge.source, "core.registry")
        }
        self.assertEqual(
            registry_consumers, {"core.ingestion.universal_ingestion"}
        )

        core_source = (CORE_ROOT / "aios_core/core.py").read_text(encoding="utf-8")
        event_source = (CORE_ROOT / "event/event_engine.py").read_text(encoding="utf-8")
        ingestion_source = (CORE_ROOT / "ingestion/universal_ingestion.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("EventDeliveryResult", core_source)
        self.assertNotIn("CoreRouteResult", event_source)
        self.assertNotIn("CoreRouteResult", ingestion_source)
        self.assertIn("core_route_result.success", ingestion_source)
        self.assertIn("core_route_result.route_target", ingestion_source)

    def test_repository_local_import_graph_has_no_cycles(self):
        graph = defaultdict(set)
        for edge in IMPORTS:
            target = _resolved_local_target(edge.target)
            if target is not None and target != edge.source:
                graph[edge.source].add(target)

        visiting = []
        visited = set()

        def visit(module):
            if module in visiting:
                start = visiting.index(module)
                cycle = visiting[start:] + [module]
                self.fail("Python import cycle: " + " -> ".join(cycle))
            if module in visited:
                return
            visiting.append(module)
            for target in sorted(graph[module]):
                visit(target)
            visiting.pop()
            visited.add(module)

        for module in sorted(MODULES):
            visit(module)

    def test_third_party_imports_are_repository_approved(self):
        approved_locations = {
            "telegram": {
                "core/adapters/telegram/main.py",
                "core/app/input_classifier.py",
                "core/ingestion/universal_ingestion.py",
                "core/pipeline/asset_pipeline.py",
                "core/storage/telegram_storage.py",
            },
            "dotenv": {"core/adapters/telegram/main.py"},
            "PIL": {"core/storage/metadata_engine.py"},
            "psycopg": {
                "core/registry/postgres_registry.py",
                "core/material_receipts/repository.py",
                "core/inventory_posting/repository.py",
            },
            "httpx": {
                "core/brain/providers/ollama.py",
                "core/brain/staging_composition.py",
            },
        }
        violations = []
        for edge in IMPORTS:
            top_level = edge.target.partition(".")[0]
            source_path = edge.source_path.relative_to(REPOSITORY_ROOT).as_posix()
            if top_level in {"core", ""} or top_level in sys.stdlib_module_names:
                continue
            if source_path not in approved_locations.get(top_level, set()):
                violations.append(edge)
        self.assertFalse(violations, _format_edges(violations))


    def test_import_time_external_startup_is_absent(self):
        forbidden_calls = {
            "connect", "run_polling", "run_webhook", "serve_forever",
            "Application.builder", "Redis", "Celery", "KafkaConsumer",
            "KafkaProducer", "create_engine",
        }
        violations = []
        for module, path in MODULES.items():
            for call in _module_level_calls(path):
                if call in forbidden_calls or call.rpartition(".")[2] in forbidden_calls:
                    violations.append(f"{module}: {call}")
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
