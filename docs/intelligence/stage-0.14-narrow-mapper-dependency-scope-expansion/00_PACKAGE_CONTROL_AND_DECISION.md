# AIOS Intelligence Stage 0.14 — Narrow Mapper Dependency Scope Expansion

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / NARROW SCOPE EXPANSION ONLY` |
| Approval baseline | `a3f3eae26b12edbf3c400e8dbf912e50dd66cc0f` |
| Existing implementation paths | exactly `2` |
| New authorized path | `tests/unit/brain/test_inference_contracts.py` |
| Total implementation/publication paths | exactly `3` |
| Architecture change | `NO` |
| Core wiring / inference | `NOT AUTHORIZED` |
| Decision | `APPROVED — READY TO RESUME IMPLEMENTATION` |

The Stage 0.14 mapper implementation passed its focused suite but the existing
reverse-dependency audit rejected its already-approved semantic boundary edge.
This package updates governance representation only. It changes no mapper,
policy test, Core/Brain implementation, runtime, service, or dependency.

The expanded implementation scope is closed to:

1. `core/core_to_brain_mapper.py`;
2. `tests/unit/core_platform/test_core_to_brain_mapper.py`; and
3. `tests/unit/brain/test_inference_contracts.py`.

No fourth path is authorized.
