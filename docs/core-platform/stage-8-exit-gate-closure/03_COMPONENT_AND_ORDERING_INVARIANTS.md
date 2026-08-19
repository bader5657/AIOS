# Component and Ordering Invariants

## RequestContext, Storage, Metadata, and Manifest

- Universal Ingestion constructs RequestContext exactly once; Adapter constructs zero; no duplicate context or business-identity promotion exists.
- File originals remain Storage-owned and precede Metadata; original binary is excluded from Registry/PostgreSQL; `Storage → App = zero`.
- Metadata retains extraction ownership and is not reinterpreted downstream.
- Manifest follows successful Metadata, contains no original binary, and remains local/atomic under its approved contract. Registry cannot precede Manifest readiness.

## Registry

- Registry stores structured registration information and references only.
- It owns one local SQL transaction. A failed transaction commits no failed row.
- Real disposable PostgreSQL evidence proves `Registry COMMIT → Event Engine`, with the committed row independently visible before handler execution.
- Registry has no retry, deduplication/idempotency, or reverse Event/Core dependency.

## Event Engine and AIOS Core

- DomainEvent is caller supplied; Registry does not synthesize it. No DomainEvent means zero Event processing.
- Event failure codes remain exactly `INVALID_ENVELOPE`, `NO_HANDLER`, and `HANDLER_FAILURE`; bounded Event failure means Core zero.
- Event Engine has no retry, broker, persistence, or Core import/invocation.
- Successful Event processing precedes exactly one `AIOSCore.route` call with the exact same immutable EventEnvelope; no reconstruction or mutation occurs.
- AIOS Core remains async, stateless, deterministic, EventEnvelope-only, and has the sole successful target `AIOS_BRAIN_BOUNDARY`.
- `route_handoff_ready` is only the approved minimal boundary-readiness projection.

## Brain exclusion

`BRAIN INVOCATION = ZERO`

Stage 8 introduced no Brain runtime, LLM/Ollama, prompts, model selection, reasoning invocation, or generated answer. Its endpoint is AIOS_BRAIN_BOUNDARY readiness.
