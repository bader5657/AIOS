# Core Platform Stage 3.1.4 Scoped Working Procedure

| Field | Value |
|---|---|
| Status | **APPROVED — PUBLICATION PENDING** |
| Approval authority | Project Owner |
| Target branch | main |
| Baseline | 852825d |
| Scope | Stage 3.1.4 only |

## Procedure

1. Confirm the Active authority and governance baseline is an ancestor of main.
2. Confirm clean tracked state and preserve unrelated untracked files.
3. Change only exact implementation targets in the Change Request.
4. Implement only ingestion-owned transitions and bounded handoff exposure.
5. Do not implement any downstream owner or excluded runtime.
6. Run focused sequence/boundary tests and repository-root regression.
7. Record exact diff, commands, results, authority trace, and exclusions.
8. Stop for Project Owner review; review is not approval.
9. After explicit approval, accept the reviewed implementation into main.
10. No later stage begins automatically.

Stop on failed test, authority conflict, missing boundary, prohibited
dependency, new canonical object need, scope expansion, downstream runtime
need, or any excluded diff. No PR rule, merge strategy, release, deployment,
version, or roadmap update is created.

## Lifecycle

| Date | State | Evidence |
|---|---|---|
| 2026-08-05 | Draft | Prepared against Active authority baseline 852825d. |
| 2026-08-05 | Proposed | Complete scoped artifact submitted for review. |
| 2026-08-05 | Reviewed | Scope, targets, exclusions, authority, dependencies, procedure, and stop conditions reviewed PASS. |
| 2026-08-05 | Approved | Project Owner instruction explicitly approves this exact scoped governance artifact; publication pending accepted commit. |
