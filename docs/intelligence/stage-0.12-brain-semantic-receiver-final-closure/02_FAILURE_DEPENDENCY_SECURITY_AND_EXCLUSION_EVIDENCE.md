# Failure, Dependency, Security, and Exclusion Evidence

Wrong receiver input raises `TypeError` before invocation. Missing/unsupported
policy raises `ValueError` before invocation. All existing failed
`InferenceResult` variants pass through by identity. Unexpected exceptions and
`asyncio.CancelledError` propagate unchanged. No pre-inference provider
`FailureCode` is manufactured.

The receiver has no Core, `EventEnvelope`, `CoreRouteResult`, concrete provider,
Ollama, HTTP/runtime/network, provider configuration, schema resolver,
schema validator, Memory, Specialist, business, service, or composition
dependency. Its only non-standard-library imports are existing Brain input,
invocation, and result contracts.

Logging, content exposure, persistence, Memory, Specialist routing, business
actions, retry, fallback, mapper behavior, Core wiring, runtime lifecycle,
live inference, and production activation are all `NONE`.

## Reviewer finding

The initial logging test observed an `asyncio` event-loop diagnostic rather
than receiver logging. The assertion was narrowed to the receiver logger while
the source audit continued to prohibit logging. Receiver behavior and scope
did not change.
