# Implementation and Type Trace

## PR and exact path trace

Implementation commit `1c2fce5bf4773a06ed0849cf8a952dffe04fc0fd`
was normal-merged by PR #119 as merge commit
`c27f233b64df744da3fa1f075328fd07cb354432`.

The implementation introduced exactly two authorized paths:

1. `core/brain/provider.py`
2. `tests/unit/brain/test_provider.py`

No third implementation path changed. Merge-baseline blobs:

| Path | Blob |
|---|---|
| `core/brain/provider.py` | `f3215ba1ee42c306f31f531d2eebfa4d8afd6c0b` |
| `tests/unit/brain/test_provider.py` | `9a0d05dde5e67f70f2cb7141cf615edb9320d9a7` |
| `core/brain/inference_contracts.py` | `931cb3e917a5515f462f9a1d7250ebc6e83ba77a` (unchanged) |
| `tests/unit/brain/test_inference_contracts.py` | `6f733ddb9d2a2704f06bcbe5e782e21d9b2331b0` (unchanged) |

## ProviderRuntimeKind

The provider-neutral string enum contains exactly:

- `LOCAL = "local"`; and
- `REMOTE = "remote"`.

There are no aliases or additional members. Classification creates no local or
remote execution authority.

## ProviderDescriptor

`ProviderDescriptor` is a frozen, slotted, defensively immutable dataclass with
exactly:

- `provider_id`;
- `model_id`;
- `runtime_kind`; and
- `capabilities`.

Both identifiers require strings of 1–128 characters, reject empty and
whitespace-only values, reject ASCII control characters U+0000–U+001F and
U+007F, and preserve accepted opaque content.

Capabilities are defensively copied to a tuple and require exact enum types.
The sole accepted value is
`(InferenceCapability.STRUCTURED_INFERENCE,)`; empty, duplicate, multiple,
unsupported, raw-string, or wrong-type capabilities fail closed.
