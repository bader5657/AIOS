# AIOS Intelligence Stage 0.19 — Narrow Staging Composition Dependency Scope Expansion

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / NARROW SCOPE EXPANSION ONLY` |
| Approval baseline | `9490bc312790c4689405e15a1b1fdf3647aa954e` |
| Existing implementation paths | exactly `2` |
| New authorized path | `tests/unit/core_platform/test_stage8_import_boundaries.py` |
| Total implementation/publication paths | exactly `3` |
| Architecture change | `NO` |
| Network / inference / Level B | `NOT AUTHORIZED` |
| Decision | `APPROVED — READY TO RESUME IMPLEMENTATION` |

The Stage 0.19 composition implementation passed its focused suite, but the
existing third-party import audit rejected the approved staging lifecycle edge
from `core/brain/staging_composition.py` to `httpx`. The repository already
pins `httpx==0.28.1`; this package adds no dependency or runtime authority.

The expanded implementation scope is closed to:

1. `core/brain/staging_composition.py`;
2. `tests/unit/brain/test_staging_composition.py`; and
3. `tests/unit/core_platform/test_stage8_import_boundaries.py`.

No fourth path is authorized.
