# Runtime, Correlation, Route, and Result Verification

Universal Ingestion remains the wiring owner and
`ingest_telegram_message(...)` remains the public entrypoint. Its existing API
is backward compatible through optional keyword-only Level A inputs.

An explicit Level A attempt exists only when
`brain_semantic_data is not None`. For the default `None` case there is no
Stage 0.16 correlation generation, Mapper call, Brain call, Brain request ID,
or inference result. Current production assembly supplies none of the Level A
semantic inputs or dependencies, so repository presence does not activate the
wiring.

For an explicit synthetic attempt, one injected/default `uuid.uuid4` factory is
called exactly once before the original EventEnvelope construction. Its exact
UUIDv4 becomes `corr-<uuid.hex>` and populates the existing correlation field at
construction. The implementation performs no envelope mutation,
reconstruction, duplicate correlation, or reroute.

The existing Core route is called once. Its exact CoreRouteResult object is
retained. A non-Brain route performs no Mapper or Brain call and creates no
Mapper-owned request ID. A Brain route without semantic data preserves only the
existing `route_handoff_ready` behavior.

For an eligible Level A route, the injected reusable CoreToBrainMapper receives
the exact route result, correlation, synthetic data, and opaque provenance
once. The Mapper remains the sole Brain request-ID owner. The exact resulting
BrainInput is passed to one injected native-async boundary call. The exact
successful or failed InferenceResult identity is retained in the additive
optional `IngestionResult.brain_result` field.

Missing explicit-attempt dependencies fail closed with `ValueError`. Mapper and
boundary TypeError/ValueError, unexpected exceptions, and cancellation
propagate unchanged. There is no retry, fallback, detached work, blocking
bridge, response emission, content logging, persistence, Memory, Specialist
routing, or business action.
