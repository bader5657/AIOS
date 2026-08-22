# AIOS Intelligence Stage 0.7 — Narrow Scope Expansion for Stage 8 httpx Import Boundary

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / SCOPE EXPANSION APPROVAL ONLY` |
| Approval baseline | `29013eafefb0d8288566ebcfe2fad3b3ee1fb403` |
| Baseline state | `HEAD == main == origin/main`; tracked worktree clean before governance branch |
| Local adapter implementation | three authorized paths; uncommitted and preserved separately |
| Focused adapter tests | `59 PASS` |
| Full-suite evidence | `573 PASS`; `58 skipped`; one Stage 8 allowlist failure |
| New authorized path | `tests/unit/core_platform/test_stage8_import_boundaries.py` |
| Total implementation/publication paths | exactly `4` |
| Scope-expansion disposition | `APPROVED — READY TO RESUME IMPLEMENTATION` |
| Runtime / Brain / production authority | `NONE` |

## Exact blocker and decision

The Stage 8 third-party import boundary correctly rejects imports absent from
its path-specific allowlist. It currently rejects the already-approved
`httpx` import from `core/brain/providers/ollama.py`. Stage 0.7 separately
approved that exact async transport, and `requirements.txt` already pins
`httpx==0.28.1`.

This package authorizes adding only the exact adapter path to the existing
`httpx` allowlist in the Stage 8 test. It does not authorize changing adapter
behavior to evade the audit, dynamic imports, broad dependency permission, or
any fifth path.

This governance package does not modify the adapter, Stage 8 test, dependency
files, runtime, Core, Brain wiring, staging, or production.

`INTELLIGENCE STAGE 0.7 NARROW SCOPE EXPANSION APPROVED — READY TO RESUME IMPLEMENTATION`
