# Post-Merge Audit Contract

Closure requires Git-resolved proof that:

1. local `main`, local `origin/main`, and remote `main` resolve to the merge;
2. all 18 package files exist on `main`;
3. the merge diff from `84fd16085970b7e7d624158ce45f1605dfe82b21`
   contains only this directory;
4. no runtime, test, SQL, schema, migration, dependency, database, Docker, or
   deployment file changed;
5. Stage 5.2.1 and Stage 5.1.x trees are unchanged;
6. Stage 3 and Stage 4 are unchanged;
7. historical `core/registry/` remains absent;
8. original-binary prohibition and future re-verification remain explicit;
9. Project Owner acceptance is present; and
10. the worktree is clean.

The actual merge SHA belongs in the final closure report. A passing audit
permits only read-only Stage 5.3.1 eligibility evaluation.
