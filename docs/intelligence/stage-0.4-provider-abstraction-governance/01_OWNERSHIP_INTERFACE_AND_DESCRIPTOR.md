# Ownership, Interface, and Descriptor

## Ownership and architecture

The provider abstraction is subordinate implementation infrastructure owned by
AIOS Brain under the existing Brain package. It is not an Intelligence layer,
AIOS Core, Specialist Router, Memory, or business workflow infrastructure.
The future module candidate is `core/brain/provider.py`, subject to separate
implementation approval. `core/intelligence/` remains prohibited.

Architecture change required: `NO`.

## InferenceProvider

The approved conceptual interface is `InferenceProvider` with exactly one
bounded operation:

```python
async def infer(request: InferenceRequest) -> InferenceResult:
    ...
```

It accepts the existing Brain-owned `InferenceRequest` and returns the existing
Brain-owned `InferenceResult`. It is async for compatibility with the current
AIOS invocation architecture. One call is one invocation boundary. The
interface provides no worker, queue, polling loop, task persistence, automatic
retry, hidden background execution, model selection, or provider-native return
object.

## ProviderDescriptor

`ProviderDescriptor` is an approved frozen, slotted, non-canonical metadata
type with exactly:

- `provider_id`;
- `model_id`;
- `runtime_kind`; and
- `capabilities`.

`provider_id` and `model_id` are bounded immutable identifiers for one
statically configured provider/model instance. Exact numeric/string bounds are
deferred to implementation approval and may not be unbounded.

`capabilities` is an immutable tuple containing exactly
`InferenceCapability.STRUCTURED_INFERENCE`: it is non-empty, has no duplicates,
and supports no discovery or broad feature matrix in v1.

Endpoint URL, API key, account identifier, credential reference, session,
mutable configuration, and business metadata are prohibited descriptor fields.

## ProviderRuntimeKind

`ProviderRuntimeKind` is a string enum with exactly:

- `LOCAL`: execution would occur on a separately approved local runtime; and
- `REMOTE`: execution would require a separately approved outbound-network
  adapter.

No additional runtime kind is approved. Classification alone grants no
installation, process, model invocation, credential, or network authority.

## Supporting-type ceiling

The complete Stage 0.4 provider abstraction type set is exactly:

1. `InferenceProvider`;
2. `ProviderDescriptor`; and
3. `ProviderRuntimeKind`.

No `ProviderExecutionResult`, `ProviderRegistry`, `ProviderRouter`,
`ModelRouter`, `ProviderFactory`, fallback manager, or retry manager is
approved.
