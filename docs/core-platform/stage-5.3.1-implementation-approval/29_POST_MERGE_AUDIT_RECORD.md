# Post-Merge Audit Contract

Activation requires Git-resolved proof that:

1. local `main`, local `origin/main`, and remote `main` resolve to the merge;
2. all 30 governance files exist on `main`;
3. the diff from `5a0cb10e10503739be1f7af8abfe4d1bdaf24493`
   contains only this governance directory;
4. no dependency, runtime, SQL, migration, test, database, configuration,
   Docker, or deployment file changed;
5. `core/registry/` and migration/test implementation paths remain absent;
6. Stage 5.1/5.2, Stage 3/4, Blueprint/Roadmap/architecture remain unchanged;
7. isolated execution authorization and production prohibition are distinct;
8. Project Owner approval is present; and
9. the worktree is clean.

The actual merge SHA belongs in the final approval report.
