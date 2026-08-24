"""Inactive lifecycle assembly for the isolated Brain staging stack."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx

from core.core_to_brain_mapper import CoreToBrainMapper

from .inference import BrainInferenceInvoker
from .inference_contracts import InferenceResult
from .input_contracts import BrainInput
from .providers.ollama import OllamaInferenceProvider, OllamaProviderConfig
from .receiver import BrainSemanticReceiver
from .schema_binding import resolve_schema, validate_schema


BrainBoundary = Callable[[BrainInput], Awaitable[InferenceResult]]
AsyncClientFactory = Callable[[], httpx.AsyncClient]


@dataclass(frozen=True, slots=True)
class IsolatedStagingComposition:
    """Narrow application-facing surface of one assembled staging lifecycle."""

    mapper: CoreToBrainMapper
    brain_boundary: BrainBoundary


@asynccontextmanager
async def create_staging_composition(
    config: OllamaProviderConfig,
    *,
    client_factory: AsyncClientFactory = httpx.AsyncClient,
) -> AsyncIterator[IsolatedStagingComposition]:
    """Assemble one inactive staging graph and close its owned HTTP client."""

    if not callable(client_factory):
        raise TypeError("client_factory must be callable")

    client = client_factory()
    if not isinstance(client, httpx.AsyncClient):
        raise TypeError("client_factory must return an httpx.AsyncClient")

    try:
        provider = OllamaInferenceProvider(
            config=config,
            client=client,
            schema_resolver=resolve_schema,
            schema_validator=validate_schema,
        )
        invoker = BrainInferenceInvoker(provider)
        receiver = BrainSemanticReceiver(invoker)
        mapper = CoreToBrainMapper()
        composition = IsolatedStagingComposition(
            mapper=mapper,
            brain_boundary=receiver.receive,
        )
        yield composition
    finally:
        await client.aclose()
