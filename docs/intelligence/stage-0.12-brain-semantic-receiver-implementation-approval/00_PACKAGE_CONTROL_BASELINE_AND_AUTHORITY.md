# AIOS Intelligence Stage 0.12 — Brain Semantic Receiver Implementation Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / IMPLEMENTATION APPROVAL ONLY` |
| Approval baseline | `828cf2c7efd9677f99c1726fd31cffdcd6008983` |
| Baseline state | `HEAD == main == origin/main`; worktree clean |
| Stage 0.11 | `BRAININPUT CONTRACT VERIFIED — ACCEPTED — CLOSED` |
| Stage 0.12 evaluation | `BOUNDARY IDENTIFIED — READY FOR GOVERNANCE APPROVAL` |
| Architecture change | `NO` |
| Implementation performed here | `NONE` |
| Decision | `APPROVED — READY TO BUILD` |

## Exact authorized implementation paths

Only these two paths are authorized:

1. `core/brain/receiver.py`
2. `tests/unit/brain/test_receiver.py`

`core/brain/__init__.py` and all existing implementation files remain
unchanged. A required third path stops implementation as
`INTELLIGENCE STAGE 0.12 SCOPE EXPANSION REQUIRED`.

This authority is repository/test-only. It grants no Core wiring, mapper,
schema resolver/validator binding, provider/runtime change, composition, live
inference, service registration, or production activation.
