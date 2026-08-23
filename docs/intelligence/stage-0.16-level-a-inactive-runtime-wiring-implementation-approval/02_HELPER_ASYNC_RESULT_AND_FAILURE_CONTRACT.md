# Helper, Async Result, and Failure Contract

## Exact continuation seam

One private native-async helper in `universal_ingestion.py` may encapsulate:

`exact CoreRouteResult + correlation ID + semantic mapping + provenance + injected Mapper + injected Brain boundary → exact InferenceResult`

It calls `CoreToBrainMapper.map()` exactly once, then awaits the injected Brain
boundary exactly once with the returned `BrainInput`. It does not reconstruct
the route result, generate a Brain request ID, create tasks, start event loops,
block, retry, or fall back.

The helper is invoked only after the existing `await aios_core.route(envelope)`
returns an exactly eligible Brain route and an explicit Level A semantic mapping
exists. For non-Brain/failed routes, or when Level A is not requested, it calls
neither Mapper nor Brain boundary.

## Result compatibility

The existing `IngestionResult` may gain one additive trailing optional field:

`brain_result: InferenceResult | None = None`

Existing callers and constructors remain compatible. Default and non-Brain
flows return `None`. An executed Level A continuation stores the exact object
returned by the async boundary without copying, translating, serializing, or
interpreting it. This is not a new DTO and creates no business-success meaning.

## Failure contract

Mapper and Brain-boundary `TypeError`/`ValueError`, unexpected exceptions, and
cancellation propagate unchanged. Failed `InferenceResult` returns unchanged
in `brain_result`. No exception is collapsed into `IngestionResult` success,
and no inference result changes registration, event, route-readiness, Telegram,
or business behavior.

Logging, persistence, Registry writes/reads for semantics, response emission,
Memory, Specialist routing, retry, fallback, and provider/runtime lifecycle are
all prohibited.
