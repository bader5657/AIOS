# Correlation, Route, and API Contract

An explicit Level A attempt exists exactly when
`brain_semantic_data is not None`. Universal Ingestion may add optional
keyword-only inputs equivalent to:

- `brain_semantic_data: Mapping[str, object] | None = None`;
- `brain_input_reference: str | None = None`;
- `brain_context_references: tuple[str, ...] = ()`;
- `brain_mapper: CoreToBrainMapper | None = None`;
- one injected native-async Brain boundary; and
- `correlation_id_factory: Callable[[], UUID] = uuid.uuid4`.

For an explicit attempt, the factory is called exactly once before the one
original EventEnvelope construction. The UUID must be v4 and is formatted as
`corr-<uuid.hex>`, retained locally, and placed in the existing
`EventEnvelope.correlation_id` field. There is no mutation, reconstruction,
second correlation ID, or second route pass.

The exact object returned by `await aios_core.route(envelope)` determines Brain
eligibility and is not reconstructed. A non-Brain or failed route may retain
the originating correlation in its envelope but causes zero Mapper calls, zero
Brain calls, zero Mapper-owned request IDs, and no inference result.

For an exact eligible Brain route, the same originating correlation ID and the
exact route result, semantic mapping, and opaque provenance are supplied once
to `CoreToBrainMapper.map`. The Mapper remains authoritative for eligibility
and sole owner of the distinct `brain-<uuid4.hex>` request ID. The resulting
exact BrainInput is passed to the async Brain boundary and awaited exactly once.

When semantic data is absent, the factory, Mapper, and Brain boundary are not
called and current production behavior remains unchanged. Explicit semantic
data with a missing Mapper or Brain boundary fails closed with `ValueError`.
No automatic projection from Telegram, Registry, Manifest, user, or business
data is authorized.
