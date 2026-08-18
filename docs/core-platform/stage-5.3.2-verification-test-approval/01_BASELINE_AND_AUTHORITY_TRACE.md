# Exact Baseline and Authority Trace

The assessment resolved local `main`, `origin/main`, and `HEAD` to:

`bf689e8272060f325fc7d6827ee476031c0c9b98`

The worktree was clean. This commit is the normal merge of Stage 5.3.1 PR #24
and contains the approved Registry runtime, migration, and tests.

| Decision | Controlling authority |
|---|---|
| Registry responsibility and containment | Stage 5.1.1 |
| Historical implementation remains rejected | Stage 5.1.2 |
| READ COMMITTED, local transaction, rollback, no retry | Stage 5.2.1 |
| Original binary exclusion | Stage 5.2.2 |
| Current runtime/API/schema | Stage 5.3.1 implementation and active approval |
| Isolation/failure verification | Execution Plan 5.3.2 and this Project Owner decision |

Blueprint, Frozen Roadmap, Authority Hierarchy, Canonical Model, Layer
Architecture, and Core Platform Execution Plan remain unchanged.
