# Result, Failure, Async, and Dependency Contract

The existing `IngestionResult` in Universal Ingestion may gain one additive
trailing field:

`brain_result: InferenceResult | None = None`

Default and ineligible flows retain `None`. An executed Level A continuation
stores the exact returned InferenceResult object without wrapping,
reinterpretation, serialization, or business-success meaning.

Mapper and Brain-boundary `TypeError` and `ValueError`, unexpected exceptions,
and `asyncio.CancelledError` propagate unchanged. A failed InferenceResult is
preserved unchanged. There is no retry, fallback, detached task, `create_task`,
`asyncio.run`, thread pool, nested loop, or blocking bridge.

Only these new dependency edges are approved:

1. runtime `core.ingestion.universal_ingestion` to
   `core.core_to_brain_mapper.CoreToBrainMapper`;
2. type-only `core.ingestion.universal_ingestion` to
   `core.brain.input_contracts.BrainInput`; and
3. type-only `core.ingestion.universal_ingestion` to
   `core.brain.inference_contracts.InferenceResult`.

Brain contract imports use `TYPE_CHECKING` where runtime imports are
unnecessary. No Receiver, Invoker, provider abstraction or implementation,
Ollama, httpx, model, endpoint, schema resolver, validator, configuration,
Memory, Specialist, or business dependency is permitted.

Inference success means inference success only. It does not complete workflow,
send Telegram output, persist state, or trigger business action. No semantic or
inference content logging is authorized; no new logging is preferred.
