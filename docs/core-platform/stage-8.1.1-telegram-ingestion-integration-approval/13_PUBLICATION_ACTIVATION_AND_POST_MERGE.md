# Publication, Activation, and Post-Merge Audit

Publication requires a reviewed PR merge containing only this governance
directory. Runtime, tests, configuration, dependencies, architecture, and prior
stage authority remain unchanged.

Upon audited merge:

- this package is **PUBLISHED**;
- its implementation approval is **ACTIVE**; and
- Stage 8.1.1 is **INTEGRATION APPROVED — READY TO BUILD** only within the exact
  authorized closed world.

Post-merge audit must confirm `HEAD == main == origin/main`, a clean worktree,
and a baseline-to-main diff containing only this governance directory. It must
also confirm no authorized future runtime/test file was modified by this PR.

Activation does not implement Stage 8.1.1, execute production Telegram, change
polling/deployment, or begin Stage 8.1.2 or later integration.
