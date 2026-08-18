# Publication, Activation, and Post-Merge Audit

Publication requires a normal PR merge containing only this governance
directory. It must not change runtime, tests, config, Domain Foundation, Stage
5, Stage 6.1/6.2 authority, dependency, schema, migration, or architecture.

Upon audited merge:

- this package is **PUBLISHED**;
- its implementation approval is **ACTIVE**; and
- Stage 6.3.1 is **IMPLEMENTATION APPROVED — READY TO BUILD** within exactly
  four paths.

Post-merge audit must confirm `main == origin/main`, the diff from baseline is
only this governance directory, `core/event/` and `tests/unit/event/` remain
absent, Stage 6.2.1/6.2.2 and Domain trees remain unchanged, and the worktree is
clean.

Activation does not implement runtime or begin Stage 6.3.2.
