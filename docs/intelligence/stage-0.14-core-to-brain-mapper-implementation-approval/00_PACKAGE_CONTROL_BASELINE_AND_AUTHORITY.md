# AIOS Intelligence Stage 0.14 — CoreToBrainMapper Implementation Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / IMPLEMENTATION APPROVAL ONLY` |
| Approval baseline | `08438d52b3cab940e9cf8d95063ff61cc16667c4` |
| Stage 0.13 | `LIVE BRAIN SEMANTIC RECEIVER VERIFIED — ACCEPTED — CLOSED` |
| Architecture change | `NO` |
| Authorized implementation paths | exactly `2` |
| Core wiring / production composition | `NOT AUTHORIZED` |
| Inference | `NOT AUTHORIZED` |
| Decision | `APPROVED — READY TO BUILD` |

This package authorizes repository-only implementation of the smallest explicit
Core-to-Brain mapper. It changes governance documentation only and does not
implement, import, construct, wire, or execute the mapper.

## Exact authorized paths

Future implementation authority is closed to exactly:

1. `core/core_to_brain_mapper.py`; and
2. `tests/unit/core_platform/test_core_to_brain_mapper.py`.

No package export, dependency, Core route, Brain contract, receiver, invoker,
provider, configuration, wiring, or third implementation path is authorized.
If a third path is required, implementation must stop for scope expansion.
