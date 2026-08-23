# AIOS Intelligence Stage 0.11 — BrainInput Contract Implementation Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / IMPLEMENTATION APPROVAL ONLY` |
| Approval baseline | `c2d7a4f957a80e8c1337959fc13e048c81ad7fbc` |
| Baseline state | `HEAD == main == origin/main`; worktree clean |
| Stage 0.10 | `VERIFIED — ACCEPTED WITH IDENTIFIER VARIANCE — CLOSED` |
| Stage 0.11 evaluation | `BOUNDARY IDENTIFIED — READY FOR GOVERNANCE APPROVAL` |
| Architecture change | `NO` |
| Implementation performed here | `NONE` |
| Decision | `APPROVED — READY TO BUILD` |

## Exact authorized implementation paths

Only these two repository paths are authorized:

1. `core/brain/input_contracts.py`
2. `tests/unit/brain/test_input_contracts.py`

`core/brain/__init__.py` is not modified. No third implementation or test path
is authorized. A required third path stops implementation with
`INTELLIGENCE STAGE 0.11 SCOPE EXPANSION REQUIRED`.

This approval authorizes a contract DTO and focused tests only. It authorizes
no mapper, receiver, Core change, invoker change, provider change, wiring,
composition, inference, runtime mutation, or production activation.
