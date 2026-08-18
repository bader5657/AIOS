# Post-Merge Audit Contract

After merge, verification must confirm:

1. `main == origin/main ==` the PR merge commit;
2. only this 21-file governance directory entered from baseline;
3. `core/domain/` tree remains
   `0cfd9fe0b1887007fad06199e427806f92837da9`;
4. `tests/unit/domain/` tree remains
   `53c45747fa5e9abd9c5f16e961b2aa1fcf8cf9fc`;
5. config blob remains
   `b1c1e8365f6ce8beadca520f471991893474bcae`;
6. Stage 6.2.1 tree remains
   `dcbabc9564d186fb72eb31a7e87e57eefb1a143f`;
7. `core/event/` and `tests/unit/event/` remain absent;
8. no runtime, test, config, dependency, architecture, or prior-stage change
   entered; and
9. worktree is clean.

All conditions are mandatory for activation and closure.
