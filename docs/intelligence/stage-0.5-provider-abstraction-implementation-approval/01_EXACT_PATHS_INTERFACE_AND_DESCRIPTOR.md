# Exact Paths, Interface, and Descriptor

## Exact authorized implementation scope

Exactly these two paths may be added in the future implementation change:

1. `core/brain/provider.py`
2. `tests/unit/brain/test_provider.py`

`core/brain/__init__.py` must not change. The existing explicit package is
sufficient and repository consumers can import the focused module directly.
No explicit package-level export is required. If any third implementation path
is necessary, implementation must stop with
`INTELLIGENCE STAGE 0.5 SCOPE EXPANSION REQUIRED`.

## InferenceProvider representation

`InferenceProvider` must be a standard-library `ABC` with exactly:

```python
@property
@abstractmethod
def descriptor(self) -> ProviderDescriptor:
    ...

@abstractmethod
async def infer(self, request: InferenceRequest) -> InferenceResult:
    ...
```

The descriptor property is required so every adapter exposes the approved
sanitized identity/capability metadata without adding invocation arguments or
mutable interface state. Both members are abstract. `infer` has no `*args`,
`**kwargs`, credential, provider configuration, model, timeout override, tool,
or other parameter. One call represents one bounded async invocation; the
abstract class implements no worker, queue, polling, background task, retry,
or runtime behavior.

## ProviderDescriptor

`ProviderDescriptor` must be `@dataclass(frozen=True, slots=True)` with exactly:

- `provider_id: str`;
- `model_id: str`;
- `runtime_kind: ProviderRuntimeKind`; and
- `capabilities: tuple[InferenceCapability, ...]`.

`provider_id` and `model_id` are opaque identifiers of 1–128 characters. They
must be actual strings, non-empty, not whitespace-only, contain no ASCII
control character U+0000–U+001F or U+007F, and preserve accepted content
exactly. No provider-specific syntax or normalization is approved.

Construction defensively converts an input list/tuple of capabilities into a
fresh tuple. The resulting tuple must be exactly
`(InferenceCapability.STRUCTURED_INFERENCE,)`. Empty, duplicate, reordered,
additional, arbitrary-string, or wrong-type capability values fail closed.

## ProviderRuntimeKind

`ProviderRuntimeKind` must use the repository string-enum convention
`class ProviderRuntimeKind(str, Enum)` with exactly:

- `LOCAL = "local"`; and
- `REMOTE = "remote"`.

No aliases or additional values are authorized. Descriptor construction
requires an actual enum member and does not coerce a string.
