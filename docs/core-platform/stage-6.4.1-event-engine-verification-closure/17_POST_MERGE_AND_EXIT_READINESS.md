# Post-Merge Audit and Exit Readiness

The closure merge must contain only this governance directory, leave runtime
and tests unchanged, synchronize `HEAD`, `main`, and `origin/main`, and leave a
clean worktree.

Read-only eligibility inspection may then establish:

`STAGE 6 READY FOR EXIT-GATE WORKFLOW`

This is eligibility only. The Stage 6 exit gate remains a separate future
workflow, and Stage 7 must not begin.
