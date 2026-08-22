# Failure, State, Dependency, and Production Boundaries

## Failure and exception behavior

Every provider-neutral failed `InferenceResult` passes through unchanged,
including all existing codes:

- `INVALID_REQUEST`
- `RUNTIME_UNAVAILABLE`
- `TIMEOUT`
- `PROVIDER_FAILURE`
- `MALFORMED_OUTPUT`
- `POLICY_DENIED`
- `RESOURCE_LIMIT`

Contract/programmer errors raised while constructing `InferenceRequest`
propagate to the caller. Unexpected provider exceptions also propagate because
the provider abstraction ordinarily returns an `InferenceResult`; the invoker
must not invent a failure mapping or new `FailureCode`.
`asyncio.CancelledError` propagates. There is no catch-all containment, retry,
fallback, second call, health preflight, or partial success.

## Dependency boundary

The approved direction is:

`core.brain.inference → InferenceProvider`

The implementation may import `InferenceRequest`, `InferenceResult`,
`InferenceCapability`, `SCHEMA_VERSION`, and `InferenceProvider`, plus standard
library typing/collection abstractions required by the signature. It must not
import `OllamaInferenceProvider`, `OllamaProviderConfig`, Core application
modules, `CoreRouteResult`, `EventEnvelope`, runtime/container/network code,
Memory, Specialists, or business domains.

## State and privacy

- logging: none in the first implementation;
- persistence: none;
- Memory: no read or write;
- Specialist Router/Specialists: no import or invocation;
- business: no action, decision, or workflow-completion semantics; and
- references: opaque provenance only and never dereferenced.

## Composition and production

Composition is constructor injection only. There is no hidden singleton,
global provider, environment lookup, endpoint/configuration, startup
registration, service wiring, Telegram connection, Core wiring, or production
inference activation. Schema resolver and validator remain provider-assembly
seams outside the invoker.

The invoker cannot start or stop Ollama, pull a model, manage keep-alive,
containers, networks, or firewalls. Implementation and tests are repository
only.
