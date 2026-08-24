# Exact Chain, Input, IDs, and Provenance

## Sole execution chain

`project_text_semantics → eligible CoreRouteResult → CoreToBrainMapper → BrainInput → create_staging_composition → BrainSemanticReceiver → BrainInferenceInvoker → OllamaInferenceProvider → repository schema binding → isolated Ollama/Qwen → InferenceResult`

Universal Ingestion and real AIOSCore routing are excluded. Use one prebuilt
CoreRouteResult with `success=True`, route target `AIOS_BRAIN_BOUNDARY`, and no
failure code or reason.

## Frozen synthetic input

Input text is exactly:

`Temperature stable and vibration within normal range.`

The projector must be called exactly once and return exactly:

```json
{"text":"Temperature stable and vibration within normal range."}
```

No Telegram, user, customer, order, invoice, transaction, product, Registry,
business, secret, production identifier, or arbitrary context data is allowed.

## Frozen identities and provenance

- correlation UUID: `20000000-0000-4000-8000-000000000020`;
- correlation ID: `corr-20000000000040008000000000000020`;
- mapper UUID: `20000000-0000-4000-8000-000000000021`;
- request ID: `brain-20000000000040008000000000000021`;
- input reference: `stage-0.20-synthetic-input-1`;
- context references: `()`.

CoreToBrainMapper remains the request-ID owner. There is no lookup,
dereference, Registry operation, or filesystem semantic input.
