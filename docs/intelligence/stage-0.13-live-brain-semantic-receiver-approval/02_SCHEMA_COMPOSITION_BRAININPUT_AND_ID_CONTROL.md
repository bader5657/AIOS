# Temporary Schema Binding, Composition, BrainInput, and ID Control

## Temporary schema binding

The uncommitted operator harness may resolve only
`brain_structured_inference_result_v1` to:

```json
{
  "type": "object",
  "properties": {
    "result": {"type": "string"}
  },
  "required": ["result"],
  "additionalProperties": false
}
```

An independent validator must require an exact one-member mapping whose
`result` value is a string. It performs no coercion, repair, default insertion,
raw-response substitution, logging, or persistence. This temporary binding is
not committed and establishes no production schema registry or composition.

## Exact temporary composition

The harness may construct only:

1. the exact resolver and independent validator;
2. one `httpx.AsyncClient`;
3. `OllamaProviderConfig`;
4. `OllamaInferenceProvider`;
5. `BrainInferenceInvoker`;
6. `BrainSemanticReceiver`; and
7. one `BrainInput`.

Test-only recording subclasses at the provider and invoker seams may delegate
to `super()` exactly once and record only calls, bounded arguments/metadata,
and returned-object identity. They may not mutate request/result content,
perform another provider request, or expose raw provider output.

## Exact BrainInput

| Field | Approved value |
|---|---|
| `schema_version` | `BRAIN_INPUT_SCHEMA_VERSION` |
| `correlation_id` | `stage-0.13-live-1` |
| `request_id` | `stage-0.13-live-request-1` |
| `intent` | `BrainIntent.STRUCTURED_INFERENCE` |
| `data` | `{"temperature_c": 25.0, "vibration": 0.12, "status": "stable"}` |
| `input_reference` | `stage-0.13-synthetic-input-1` |
| `context_references` | `()` |

The harness constants must be compared for exact equality with both approved
ID literals immediately before calling the receiver. Any mismatch aborts
before inference. Downstream IDs are taken only from `BrainInput`; no duplicate
manual invoker/provider ID values are allowed.
