# Publication, Activation, and Execution Sequence

## Publication and activation

- Branch: `governance/stage-9.2.4-security-exclusion-audit-approval`
- Base: `a5ce9b45c03a3d06098e29b3dec604caac1f4c73`
- Scope: files in this governance package only
- Activation: normal merge of its clean, mergeable PR to `main`
- Production access or mutation during approval: `NONE`

Before merge, review must confirm a governance-only diff; exact baseline and
authority; no protected content; no `.gitignore`, code, test, deployment,
runtime, database, Storage, Blueprint, or Roadmap change; and a clean,
mergeable PR.

After merge, audit must confirm `HEAD == main == origin/main`, a clean
worktree, the complete package on `main`, unchanged implementation artifacts,
no production mutation, and no Stage 9.3.1 work.

## Controlled next sequence

1. Create a separate `.gitignore`-only implementation branch and PR using
   exactly `02_GITIGNORE_AUDIT_AND_EXACT_HARDENING_AUTHORITY.md`.
2. Complete and accept its closed-world verification.
3. Through `Bagus-PC → aiosadmin@aios-prod-01`, collect the separately
   attributable read-only runtime evidence authorized by
   `03_OPERATOR_READ_ONLY_RUNTIME_AUDIT_AUTHORITY.md`.
4. Perform the bounded non-disclosing history scan and journal category audit.
5. Build a separate Stage 9.2.4 verification closure package.

Repository hardening precedes runtime evidence collection. The streams must
retain separate baselines and evidence even if a later explicit execution
authority schedules them together.

`STAGE 9.2.4 SECURITY/EXCLUSION AUDIT APPROVED — READY FOR CONTROLLED HARDENING AND VERIFICATION`
