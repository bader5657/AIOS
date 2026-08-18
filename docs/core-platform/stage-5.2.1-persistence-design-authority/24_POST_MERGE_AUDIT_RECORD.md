# Post-Merge Audit Contract

Closure requires Git-resolved proof that:

1. local `main`, local `origin/main`, and remote `main` resolve to the merge;
2. all 25 package files exist on `main`;
3. the merge diff from `2b442d90e72eb9f69c46bb615987ffce16c88d2b`
   contains only this directory;
4. no runtime, test, schema, migration, SQL, configuration, dependency,
   PostgreSQL, Docker, deployment, or production file changed;
5. `core/registry/` remains absent;
6. Stage 5.1.1 and Stage 5.1.2 trees remain unchanged;
7. Stage 3 and Stage 4 remain unchanged;
8. Registry Entry remains explicitly unresolved;
9. Project Owner approval and original-binary prohibition remain present; and
10. the worktree is clean.

The actual merge SHA belongs in the final closure report. A passing audit
permits only read-only Stage 5.2.2 eligibility evaluation.
