# Implementation, Request, Invocation, and Result Trace

## Constructor and provider abstraction

`BrainInferenceInvoker` exists in `core/brain/inference.py`. Its constructor
accepts exactly one `InferenceProvider`, validates that abstract type, and
stores it for injection. It does not import, construct, discover, select, or
configure `OllamaInferenceProvider` or any other concrete provider.

## Public invocation contract

The sole public operation is keyword-only `async invoke(...) ->
InferenceResult`. It constructs exactly one authoritative `InferenceRequest`:

- `schema_version` is fixed internally to `SCHEMA_VERSION`;
- `capability` is fixed internally to
  `InferenceCapability.STRUCTURED_INFERENCE`;
- `input_payload` is exactly
  `{"instruction": instruction, "data": data}`;
- `instruction` is passed unchanged;
- `data` is a provider-neutral `Mapping[str, object]`, with the immutable
  snapshot owned by `InferenceRequest`;
- `correlation_id` and `request_id` are preserved;
- `timeout_ms` is passed to authoritative `InferenceRequest` validation;
- `output_schema_ref` is passed unchanged; and
- `input_reference` and `context_references` remain opaque and unchanged.

There is no caller override for schema version, capability, or arbitrary input
payload.

## Provider invocation and result identity

The implementation performs exactly one provider operation:

```python
return await self._provider.infer(request)
```

There is no health preflight, second provider call, retry, fallback, routing,
or provider selection. The exact received `InferenceResult` is returned by
identity without copying, wrapping, normalization, failure rewriting,
business interpretation, or success reinterpretation.
