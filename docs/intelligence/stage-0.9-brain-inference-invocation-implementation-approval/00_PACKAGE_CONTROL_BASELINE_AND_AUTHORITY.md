# AIOS Intelligence Stage 0.9 — Brain Inference Invocation Implementation Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / IMPLEMENTATION APPROVAL ONLY` |
| Approval baseline | `60ffe7ed6d0b350242f017eb3d2e16c782129680` |
| Baseline state | `HEAD == main == origin/main`; worktree clean |
| Stage 0.8 | `LIVE STAGING INTEGRATION VERIFIED — ACCEPTED — CLOSED` |
| Architecture change | `NO` |
| Authorized implementation paths | exactly `2` |
| Production inference | `NOT AUTHORIZED` |
| Core-to-Brain wiring | `NOT AUTHORIZED` |
| Live Brain staging invocation | `NOT AUTHORIZED` |

## Decision

Repository-only implementation of the first Brain-owned inference invocation
seam is approved at exactly:

1. `core/brain/inference.py`
2. `tests/unit/brain/test_inference.py`

`core/brain/__init__.py` is not authorized. Existing repository convention
imports Brain contracts and provider abstractions from their defining
submodules; no package-root export is required.

The implementation may construct one provider-neutral `InferenceRequest`, call
one injected `InferenceProvider` exactly once, and return the exact
`InferenceResult` object unchanged. This package creates governance records
only. It implements no invoker and executes no inference.

## Closed-world scope

Any required third implementation path, Core change, concrete Ollama import,
canonical contract change, composition root, new dependency, Memory,
Specialist, business logic, or live inference stops implementation and returns
to governance as `INTELLIGENCE STAGE 0.9 SCOPE EXPANSION REQUIRED`.
