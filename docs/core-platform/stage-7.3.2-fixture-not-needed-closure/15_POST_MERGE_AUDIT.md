# Post-Merge Audit

After closure merge, verification must confirm:

1. `HEAD == main == origin/main`;
2. the worktree is clean;
3. this complete governance directory exists on `main`;
4. the closure PR introduced only this directory; and
5. no runtime, test, configuration, dependency, infrastructure, Blueprint,
   Roadmap, or architecture change entered through the closure.

Failure of any condition blocks closure activation.
