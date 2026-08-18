# Post-Merge Audit Contract

Activation requires Git-resolved proof that:

1. local `main`, `origin/main`, and the merged PR resolve consistently;
2. all 20 governance files exist on `main`;
3. the diff from `c4fde41a6f96763d6252922118780c922d6b4b1c` contains only this directory;
4. no runtime, test, dependency, schema, migration, configuration, database,
   Docker, deployment, or earlier authority file changed;
5. Manifest path identity and reference decisions remain exact;
6. the four-path closed scope and isolated-only authorization remain intact;
7. production prohibition and Project Owner approval are present;
8. no Stage 5.4.1 implementation entered the governance PR; and
9. the worktree is clean.

Passing this audit activates the approval and makes Stage 5.4.1 ready for a
separate implementation workflow. The merge SHA belongs in the final report.
