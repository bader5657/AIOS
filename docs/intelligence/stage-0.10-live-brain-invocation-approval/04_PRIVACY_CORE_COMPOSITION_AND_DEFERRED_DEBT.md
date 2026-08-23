# Privacy, Core, Composition, and Deferred Debt

## Logging and persistence

No content logging or persistence is authorized. The instruction, data, raw
provider response, and structured output must not be written to repository,
files, databases, service logs, telemetry, Memory, Registry, or other state.
The operator terminal may display the bounded synthetic result only for
immediate validation; durable evidence must retain bounded metadata, counts,
identities, status/failure code, timing, validation outcome, and safety state,
not content or raw response.

## Dependency and Core boundary

The dependency direction remains:

`BrainInferenceInvoker → InferenceProvider → injected OllamaInferenceProvider`

`BrainInferenceInvoker` remains unaware of Ollama. Stage 0.9 implementation is
unchanged. The harness starts from explicit Brain-local arguments and must not
consume `CoreRouteResult` or `EventEnvelope`, modify Core, connect Telegram,
or invoke Registry, Event Engine, Memory, Specialist Router/Specialists,
business workflows, or tools.

## Deferred Core handoff debt

The Core-to-Brain semantic receiver/input contract remains unresolved. The
current Core readiness marker is not sufficient semantic Brain input. This
live interoperability test neither exercises nor resolves that debt, and no
Core wiring is authorized.

## Deferred composition debt

The concrete outer production location that assembles provider configuration,
schema resolver, schema validator, provider, and invoker remains unresolved.
The temporary operator harness is explicitly non-production composition and
must not become a hidden singleton, service locator, registry, startup hook,
or composition root. Stage 0.10 does not close composition debt.

## Production boundary

No production composition, inference, activation, traffic, lifecycle control,
deployment, or service integration is authorized.
