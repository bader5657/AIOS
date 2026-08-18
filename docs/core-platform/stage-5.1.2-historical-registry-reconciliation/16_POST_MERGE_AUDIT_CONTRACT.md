# Post-Merge Audit Contract

Closure requires Git-resolved verification that:

1. local `main`, local `origin/main`, and remote `main` resolve to the merge;
2. the complete package exists on `main`;
3. the merge diff from `347b81f501c4fb2981c851cbdfec23d2c29a95c4`
   contains only this directory;
4. `core/registry/` and `tests/unit/registry/` remain absent;
5. no runtime, test, schema, configuration, PostgreSQL, or dependency file
   changed;
6. the Stage 5.1.1 tree is byte-identical to the reconciliation baseline;
7. Stage 3 and Stage 4 trees are unchanged;
8. the Project Owner decision and `REJECT — REAFFIRMED` are present; and
9. the worktree is clean.

The merge SHA and audit results are reported after actual merge; no future SHA
is fabricated in this governance record. A passing audit permits only a
read-only Stage 5.2.1 eligibility evaluation and does not start it.
