# Publication, Activation, and Post-Merge Audit

Publication requires a normal reviewed PR merge containing only this governance
directory. Runtime, tests, configuration, architecture, Domain Foundation,
Stage 5, Stage 6, and active Stage 7.1/7.2 authority must remain unchanged.

Upon audited merge:

- this package is **PUBLISHED**;
- its implementation approval is **ACTIVE**; and
- Stage 7.3.1 is **IMPLEMENTATION APPROVED — READY TO BUILD** within exactly
  four paths.

Post-merge audit must confirm `HEAD == main == origin/main`, a clean worktree,
and a baseline-to-main diff containing only this governance directory. It must
also confirm that `core/aios_core/` and `tests/unit/aios_core/` remain absent.

Activation does not implement AIOS Core, begin Stage 7.3.2, or begin Stage 8
integration.
