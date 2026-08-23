# Exact API, Correlation, Semantics, and Provenance

## Backward-compatible Level A inputs

The existing public async entrypoint remains
`core.ingestion.universal_ingestion.ingest_telegram_message`. Its existing
positional parameters and default behavior remain unchanged. Level A may add
only keyword-only optional inputs equivalent to:

- `brain_mapper: CoreToBrainMapper | None = None`;
- `brain_boundary: BrainBoundaryHandler | None = None`;
- `semantic_data: Mapping[str, object] | None = None`;
- `input_reference: str | None = None`;
- `context_references: tuple[str, ...] = ()`; and
- `correlation_id_factory: Callable[[], UUID] = uuid4`.

`semantic_data is not None` is the sole explicit request for Level A Brain
continuation. When it is `None`, no correlation ID is generated for Brain, no
Mapper/Brain dependency is required, the existing EventEnvelope correlation
behavior remains `None`, and current production behavior is unchanged. If it
is supplied without both Mapper and Brain boundary dependencies, fail closed
with `ValueError`; do not infer or partially activate.

## Correlation and EventEnvelope

For one explicit Level A request, Universal Ingestion calls the injected
standard-library UUIDv4 factory exactly once after accepting ingress identity,
formats `corr-<uuid.hex>`, and retains it in one local immutable orchestration
variable. Invalid factory/type/version output fails before Brain invocation.

The same value populates the already-existing `EventEnvelope.correlation_id`
field and later enters Mapper unchanged. This sets an existing optional field;
it changes neither EventEnvelope schema nor `AIOSCore`. Non-Level-A execution
continues constructing the envelope with `None` as today.

## Semantic data and provenance

Level A accepts only explicitly caller-supplied synthetic provider-neutral
semantic mappings. It never derives data from Telegram text/caption,
RequestContext, pipeline metadata, Manifest contents, Registry rows, or
business objects.

`input_reference` and `context_references` are explicit caller-supplied opaque
values. Level A performs no lookup, path conversion, dereference, or automatic
Manifest/Registry mapping. The Mapper remains authoritative for BrainInput
validation and immutable snapshot construction.
