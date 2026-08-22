# Class, Signature, Request, and Result Contract

## Class and constructor

The implementation defines one minimal class:

```python
class BrainInferenceInvoker:
    def __init__(self, provider: InferenceProvider) -> None: ...
```

The constructor receives exactly one `InferenceProvider`. It stores that
abstract dependency for constructor injection. It must not create or discover a
provider, inspect a concrete provider, maintain a registry or routing table, or
hold fallback providers.

## Public async seam

The sole public invocation method is:

```python
async def invoke(
    self,
    *,
    correlation_id: str,
    request_id: str,
    instruction: str,
    data: Mapping[str, object],
    timeout_ms: int,
    output_schema_ref: str,
    input_reference: str | None = None,
    context_references: tuple[str, ...] = (),
) -> InferenceResult: ...
```

There is no new Brain input DTO. `schema_version` is not caller-selectable: the
invoker uses the authoritative `SCHEMA_VERSION` constant. Capability is not
caller-selectable: the invoker uses
`InferenceCapability.STRUCTURED_INFERENCE`.

## Exact request construction

The method constructs exactly one `InferenceRequest` with:

- the fixed current schema version and capability;
- caller values for both IDs, timeout, schema reference, and optional opaque
  references; and
- `input_payload={"instruction": instruction, "data": data}` exactly.

It performs no prompt rewriting, coercion, schema resolution, dereference,
Registry/Storage/Memory lookup, provider configuration, deadline derivation, or
retry preparation. Existing `InferenceRequest` validation and the provider's
accepted Stage 0.7 payload enforcement remain authoritative.

## Invocation and result

The implementation performs exactly:

```python
result = await self._provider.infer(request)
return result
```

The provider is called once. The result is returned by identity without copy,
normalization, failure-code rewriting, exception conversion, or success
interpretation.
