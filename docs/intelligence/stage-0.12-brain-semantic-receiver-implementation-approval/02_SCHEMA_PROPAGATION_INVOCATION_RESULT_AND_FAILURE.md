# Schema, Propagation, Invocation, Result, and Failure Contract

## Schema semantics and separation

The selected `brain_structured_inference_result_v1` reference has this exact
later-bound semantic expectation:

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

For Stage 0.12 implementation authority, this exact shape ratifies and
supersedes the evaluation candidate's additional string-length constraints.
The existing inference-result encoded-size bound remains applicable.

The receiver passes only the reference. It contains no schema contents,
resolver, validator, schema registry, or provider-native format. Future
composition must bind resolver/validator behavior under separate authority.

## Direct propagation and ID control

The single invoker call receives directly:

- `correlation_id=brain_input.correlation_id`;
- `request_id=brain_input.request_id`;
- `data=brain_input.data`;
- `input_reference=brain_input.input_reference`; and
- `context_references=brain_input.context_references`.

Instruction, timeout, and schema reference come only from the selected private
policy. The public method accepts no duplicate identifiers or overrides.
Therefore `ID_MISMATCH_STRUCTURALLY_PREVENTED`; no post-hoc equality comparison
is required.

Data and references pass semantically unchanged without mutation, enrichment,
retrieval, dereference, provider shaping, prompt insertion, or configuration.
The unchanged `BrainInferenceInvoker` remains responsible for constructing the
standard instruction/data inference payload.

## Invocation, result, and failure

The receiver performs exactly one `await self._invoker.invoke(...)` and returns
that exact object. Successful and failed `InferenceResult` objects pass by
identity without inspection, wrapper, normalization, retry, or business
interpretation.

Wrong `BrainInput` type raises `TypeError`. Missing/unsupported policy raises
`ValueError` before invocation. No provider `FailureCode` is manufactured.
Unexpected exceptions and `asyncio.CancelledError` propagate unchanged. There
is no retry, fallback, catch-all conversion, or second call.
