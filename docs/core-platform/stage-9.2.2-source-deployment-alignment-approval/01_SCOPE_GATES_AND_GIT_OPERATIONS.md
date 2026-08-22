# Scope, Gates, and Authorized Git Operations

Before source mutation, the executor must verify all of the following:

- host identity is `aiosadmin@aios-prod-01`;
- `aios.service` remains active with exactly one Telegram polling process;
- the predecessor branch and SHA are recorded;
- the local `.gitignore`-only patch is stored outside `/opt/aios-src` with a
  recorded SHA-256;
- the exact target commit exists, belongs to approved `main` history, and
  contains the Stage 8 closure, Stage 9.1.1 closure, Stage 9.1.2 closure,
  Stage 9.2.1 service artifact, and Stage 9.2.2 approval;
- there are no other tracked modifications or untracked production data that
  checkout would lose; and
- rollback to the predecessor SHA is documented.

After those gates pass, the only authorized Git mutations in `/opt/aios-src`
are fetch from the existing `origin` and checkout of detached exact commit
`4168e098612c930215a49028d4ca9fc200d21cfd`. Detached deployment is selected
because publication of this governance package advances `main` beyond the
exact approved deployment baseline. No release branch may be invented.

The resulting worktree must be clean. The preserved `.gitignore` patch must
not be reapplied without separate approval.

