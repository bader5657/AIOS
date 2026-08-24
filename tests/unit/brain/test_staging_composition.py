"""Tests for the inactive Stage 0.19 isolated staging composition."""

from __future__ import annotations

import ast
import asyncio
from collections.abc import Callable
import inspect
from pathlib import Path

import httpx
import pytest

from core.brain import staging_composition as module
from core.brain.providers.ollama import (
    APPROVED_KEEP_ALIVE,
    APPROVED_MODEL_ID,
    APPROVED_TIMEOUT_CEILING_MS,
    OllamaProviderConfig,
)
from core.brain.schema_binding import resolve_schema, validate_schema
from core.core_to_brain_mapper import CoreToBrainMapper


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "core/brain/staging_composition.py"
BASE_URL = "http://172.31.63.2:11434"


def make_config() -> OllamaProviderConfig:
    return OllamaProviderConfig(
        base_url=BASE_URL,
        model_id=APPROVED_MODEL_ID,
        timeout_ceiling_ms=APPROVED_TIMEOUT_CEILING_MS,
        keep_alive=APPROVED_KEEP_ALIVE,
    )


class RecordingClient(httpx.AsyncClient):
    def __init__(self) -> None:
        self.request_count = 0
        self.close_count = 0

        def reject_request(request: httpx.Request) -> httpx.Response:
            self.request_count += 1
            raise AssertionError(f"unexpected HTTP request: {request.url}")

        super().__init__(transport=httpx.MockTransport(reject_request))

    async def aclose(self) -> None:
        self.close_count += 1
        await super().aclose()


class ClientFactory:
    def __init__(self) -> None:
        self.calls = 0
        self.clients: list[RecordingClient] = []

    def __call__(self) -> httpx.AsyncClient:
        self.calls += 1
        client = RecordingClient()
        self.clients.append(client)
        return client


def run(coroutine: object) -> object:
    return asyncio.run(coroutine)  # type: ignore[arg-type]


def test_composition_builds_exact_graph_once_without_activity() -> None:
    async def scenario() -> None:
        config = make_config()
        factory = ClientFactory()

        async with module.create_staging_composition(
            config, client_factory=factory
        ) as composition:
            assert factory.calls == 1
            assert len(factory.clients) == 1
            client = factory.clients[0]
            assert not client.is_closed
            assert client.request_count == 0

            assert isinstance(composition, module.IsolatedStagingComposition)
            assert isinstance(composition.mapper, CoreToBrainMapper)
            assert inspect.iscoroutinefunction(composition.brain_boundary)
            receiver = composition.brain_boundary.__self__
            assert isinstance(receiver, module.BrainSemanticReceiver)
            invoker = receiver._invoker
            assert isinstance(invoker, module.BrainInferenceInvoker)
            provider = invoker._provider
            assert isinstance(provider, module.OllamaInferenceProvider)
            assert provider._config is config
            assert provider._client is client
            assert provider._schema_resolver is resolve_schema
            assert provider._schema_validator is validate_schema
            assert client.request_count == 0

        assert factory.calls == 1
        assert client.is_closed
        assert client.close_count == 1
        assert client.request_count == 0

    run(scenario())


def test_explicit_config_is_required_and_factory_is_lazy() -> None:
    signature = inspect.signature(module.create_staging_composition)
    assert signature.parameters["config"].default is inspect.Parameter.empty
    assert signature.parameters["client_factory"].default is httpx.AsyncClient

    factory = ClientFactory()
    context = module.create_staging_composition(make_config(), client_factory=factory)
    assert factory.calls == 0

    async def enter_and_exit() -> None:
        async with context:
            assert factory.calls == 1

    run(enter_and_exit())


def test_public_surface_is_only_mapper_and_brain_boundary() -> None:
    assert [field.name for field in module.IsolatedStagingComposition.__dataclass_fields__.values()] == [
        "mapper",
        "brain_boundary",
    ]
    assert module.IsolatedStagingComposition.__slots__ == (
        "mapper",
        "brain_boundary",
    )


def test_two_composition_lifecycles_do_not_share_objects() -> None:
    async def scenario() -> None:
        factory = ClientFactory()
        async with module.create_staging_composition(
            make_config(), client_factory=factory
        ) as first:
            first_mapper = first.mapper
            first_boundary = first.brain_boundary
        async with module.create_staging_composition(
            make_config(), client_factory=factory
        ) as second:
            assert second.mapper is not first_mapper
            assert second.brain_boundary is not first_boundary
        assert factory.calls == 2
        assert all(client.close_count == 1 for client in factory.clients)

    run(scenario())


@pytest.mark.parametrize(
    "failing_name",
    [
        "OllamaInferenceProvider",
        "BrainInferenceInvoker",
        "BrainSemanticReceiver",
        "CoreToBrainMapper",
        "IsolatedStagingComposition",
    ],
)
def test_partial_construction_failure_closes_client_and_propagates_original(
    monkeypatch: pytest.MonkeyPatch,
    failing_name: str,
) -> None:
    original = RuntimeError(f"{failing_name} construction failed")

    def fail(*args: object, **kwargs: object) -> object:
        raise original

    monkeypatch.setattr(module, failing_name, fail)
    factory = ClientFactory()
    escaped: list[object] = []

    async def scenario() -> None:
        with pytest.raises(RuntimeError) as captured:
            async with module.create_staging_composition(
                make_config(), client_factory=factory
            ) as composition:
                escaped.append(composition)
        assert captured.value is original

    run(scenario())
    assert escaped == []
    assert factory.calls == 1
    assert factory.clients[0].close_count == 1
    assert factory.clients[0].is_closed
    assert factory.clients[0].request_count == 0


def test_context_exception_propagates_and_closes_client() -> None:
    original = ValueError("context failure")
    factory = ClientFactory()

    async def scenario() -> None:
        with pytest.raises(ValueError) as captured:
            async with module.create_staging_composition(
                make_config(), client_factory=factory
            ):
                raise original
        assert captured.value is original

    run(scenario())
    assert factory.clients[0].close_count == 1
    assert factory.clients[0].is_closed


def test_cancellation_propagates_after_client_cleanup() -> None:
    cancellation = asyncio.CancelledError()
    factory = ClientFactory()

    async def scenario() -> None:
        with pytest.raises(asyncio.CancelledError) as captured:
            async with module.create_staging_composition(
                make_config(), client_factory=factory
            ):
                raise cancellation
        assert captured.value is cancellation

    run(scenario())
    assert factory.clients[0].close_count == 1
    assert factory.clients[0].is_closed


@pytest.mark.parametrize("factory", [None, 1, object()])
def test_non_callable_client_factory_fails_before_client_creation(
    factory: object,
) -> None:
    async def scenario() -> None:
        with pytest.raises(TypeError, match="client_factory must be callable"):
            async with module.create_staging_composition(
                make_config(), client_factory=factory  # type: ignore[arg-type]
            ):
                raise AssertionError("composition must not be yielded")

    run(scenario())


def test_invalid_client_factory_result_fails_closed() -> None:
    calls = 0

    def invalid_factory() -> object:
        nonlocal calls
        calls += 1
        return object()

    async def scenario() -> None:
        with pytest.raises(
            TypeError, match="client_factory must return an httpx.AsyncClient"
        ):
            async with module.create_staging_composition(
                make_config(),
                client_factory=invalid_factory,  # type: ignore[arg-type]
            ):
                raise AssertionError("composition must not be yielded")

    run(scenario())
    assert calls == 1


def test_module_has_only_approved_imports_and_no_projector() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MODULE_PATH))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    direct_imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert direct_imports == {"httpx"}
    assert imported == {
        "__future__",
        "collections.abc",
        "contextlib",
        "dataclasses",
        "core.core_to_brain_mapper",
        "inference",
        "inference_contracts",
        "input_contracts",
        "providers.ollama",
        "receiver",
        "schema_binding",
    }
    assert "semantic_projection" not in source
    assert "project_text_semantics" not in source


def test_module_contains_no_activation_or_side_effect_ownership() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    prohibited = (
        "universal_ingestion",
        "aioscore",
        "eventengine",
        "telegram",
        "registry",
        "database",
        "filesystem",
        "pathlib",
        "memory",
        "specialist",
        "core.domain",
        "getenv",
        "environ",
        "load_dotenv",
        "logging",
        "logger",
        "persist",
        "docker",
        "firewall",
        "api/version",
        "api/ps",
        "health",
        "pull",
        "preload",
        "unload",
        "run_polling",
        "aios.service",
        BASE_URL,
    )
    assert not [marker for marker in prohibited if marker in source]


def test_production_startup_does_not_import_staging_composition() -> None:
    production_paths = (
        ROOT / "core/adapters/telegram/main.py",
        ROOT / "core/ingestion/universal_ingestion.py",
        ROOT / "deploy/systemd/aios.service",
    )
    for path in production_paths:
        assert "staging_composition" not in path.read_text(encoding="utf-8")
