# Exact Harness, Request, Schema, and Result Contract

## Temporary operator-side composition

One uncommitted operator-side harness, outside the repository or under `/tmp`,
may construct only:

1. a bounded schema resolver;
2. a bounded independent validator;
3. one `httpx.AsyncClient` using accepted `httpx==0.28.1`;
4. `OllamaProviderConfig`;
5. `OllamaInferenceProvider`; and
6. `BrainInferenceInvoker` with that adapter injected as `InferenceProvider`.

This is test-harness composition only. It must not be installed, committed,
registered, persisted, imported by production, or treated as resolution of the
outer production composition boundary.

## Exact invocation

The harness must call `await invoker.invoke(...)` exactly once. It must not call
`provider.infer(...)` directly. Use these fixed Brain-local arguments:

- `correlation_id`: `stage-0.10-live-1`
- `request_id`: `stage-0.10-live-request-1`
- `instruction`: `Classify one synthetic sensor record as normal or warning. Return only the requested structured fields.`
- `data`: `{"temperature_c": 25.0, "vibration": 0.12, "status": "stable"}`
- `timeout_ms`: `120000`
- `output_schema_ref`: `stage_0_10_sensor_classification_v1`
- `input_reference`: `stage-0.10-synthetic-sensor-1`
- `context_references`: `()`

The provider-side request must originate naturally from
`BrainInferenceInvoker`: authoritative `SCHEMA_VERSION`, fixed
`STRUCTURED_INFERENCE`, preserved IDs, exact instruction/data payload,
timeout, schema reference, and opaque optional references. The harness must not
inspect or mutate an internal request to force success.

## Resolver and independent validator

The resolver accepts only `stage_0_10_sensor_classification_v1` and returns:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["category", "confidence"],
  "properties": {
    "category": {"type": "string", "enum": ["normal", "warning"]},
    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
  }
}
```

The independent validator separately requires an exact two-member mapping,
category `normal` or `warning`, and a finite non-Boolean numeric confidence in
`0.0..1.0`. It performs no coercion, repair, default insertion, or raw-response
substitution. Provider-side format enforcement is defense in depth, not the
independent validation.

## PASS criteria and identity evidence

PASS requires all of the following:

- the invoker is called exactly once;
- the provider is invoked exactly once;
- the adapter sends exactly one live provider request;
- `success is True` and `failure_code is None`;
- `provider_id == "ollama-local"`;
- `model_id == "qwen2.5:1.5b-instruct-q4_K_M"`;
- correlation and request IDs are preserved;
- structured output is present and independently validates;
- duration is valid;
- no raw response is exposed;
- no Brain-local rewrite, normalization, wrapper, or duplicate DTO occurs;
- the exact provider `InferenceResult` identity reaches the caller; and
- no retry or fallback occurs.

Identity may be proven by a test-harness-only recording proxy/subclass at the
injected provider boundary that records call count and returned object without
changing request/result content or making an additional provider request.
