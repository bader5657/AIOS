# Semantic Input, Provenance, Result, and Failures

## Missing authoritative caller inputs

`CoreToBrainMapper.map()` requires the exact `CoreRouteResult`,
`correlation_id`, provider-neutral semantic `data`, `input_reference`, and
`context_references`.

The exact route result is available and must be passed unchanged. The other
values are not presently authorized runtime outputs:

- `RequestContext` has no correlation-ID field;
- Universal Ingestion constructs `EventEnvelope(correlation_id=None)`, and
  tests explicitly preserve that value;
- pipeline metadata is descriptive asset metadata, not an approved semantic
  inference projection;
- Telegram text/caption is transport content and cannot be forwarded blindly;
- a Manifest path and Registry record ID exist in some successful flows, but no
  authority assigns them to Brain `input_reference` or `context_references`.

The wiring must not generate a second identifier, repurpose event IDs, invent a
correlation ID, treat arbitrary Telegram content as semantic data, or silently
promote storage/Registry identifiers into Brain provenance. A separate semantic
ingress decision must define the originating correlation-ID policy, the exact
provider-neutral mapping, and the authoritative opaque-reference mapping.

## Result and failure separation

The preferred initial result behavior is direct return of the unchanged
`InferenceResult` to the orchestration caller. No new DTO, business success,
acknowledgement text, persistence, or downstream business action is justified.
The existing `IngestionResult` has no Brain-result field, so the final result
destination remains an explicit approval decision rather than an implicit
extension.

Mapper `TypeError`/`ValueError`, receiver/policy `TypeError`/`ValueError`, and
provider-returned `InferenceResult` failures are three distinct categories.
They must propagate without collapse, retry, fallback, or false success. A
successful result must not update orders, transactions, inventory, workflow
completion, or automated business responses.

Logging is `NONE` by default. If later authorized, it is metadata-only:
correlation ID, mapper-owned request ID, boundary transition, and bounded
success/failure code. Semantic data, instruction/prompt, structured output, and
raw provider response must never be logged.
