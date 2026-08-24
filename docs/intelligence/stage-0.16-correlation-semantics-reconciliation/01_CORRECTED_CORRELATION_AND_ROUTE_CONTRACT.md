# Corrected Correlation and Route Contract

## Explicit Level A attempt

An explicit Level A continuation attempt exists exactly when
`brain_semantic_data is not None`. This fact is available before the original
EventEnvelope is constructed.

When semantic data is `None`, Universal Ingestion generates no Stage 0.16
correlation ID, preserves the existing `EventEnvelope.correlation_id` behavior,
and calls neither Mapper nor Brain boundary.

When semantic data is not `None`, Universal Ingestion must:

1. call the injected UUIDv4 factory exactly once before EventEnvelope
   construction;
2. format the result exactly as `corr-<uuid4.hex>`;
3. retain it in one local orchestration variable;
4. populate the existing `EventEnvelope.correlation_id` during the original
   construction; and
5. reuse that exact value if routing later permits Brain continuation.

There is no post-construction mutation, envelope reconstruction, second routing
pass, correlation regeneration, or second originating correlation ID.

## Route eligibility remains authoritative

Correlation identifies the originating explicit Level A attempt. It does not
authorize Brain execution. The exact result returned by
`await aios_core.route(envelope)` remains authoritative for eligibility.

For a non-Brain or failed route, the envelope may retain the originating
correlation ID, but Mapper and Brain boundary calls remain zero and no Mapper
request ID or InferenceResult is produced.

For an eligible `AIOS_BRAIN_BOUNDARY` route, the exact same correlation value
passes to `CoreToBrainMapper.map`, the resulting BrainInput, the injected async
Brain boundary, and the returned InferenceResult contract. Universal Ingestion
does not create a Brain request ID. `CoreToBrainMapper` alone creates the
distinct `brain-<uuid4.hex>` request ID after route eligibility succeeds.
