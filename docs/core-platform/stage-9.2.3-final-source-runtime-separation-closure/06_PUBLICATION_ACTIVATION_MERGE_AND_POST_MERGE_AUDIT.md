# Publication, Activation, Merge, and Post-Merge Audit

## Publication and activation

- Dedicated branch:
  `governance/stage-9.2.3-final-source-runtime-separation-closure`
- Exact base: `ca1fc773b4648710932b9e77b64fd1a475cbbc4f`
- Publication scope: files in this closure directory only
- Production access or mutation during closure: `NONE`
- Activation rule: normal merge of the dedicated governance PR to `main`

## Governance-only review gate

Before merge, review must prove:

- the branch differs from its base only under this closure directory;
- `deploy/systemd/aios.service` remains blob
  `8794ee77cea44dae5bb7f96d876d3a240b5a78ed` and SHA-256
  `02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281`;
- the focused test remains blob
  `f25781069aa3846088213ac3181dac856ba11b1d`;
- no tests, Python, `runtime.env`, Docker Compose, PostgreSQL, Storage,
  production state, Blueprint, or Roadmap changed;
- the package contains no secret value; and
- the PR is `CLEAN / MERGEABLE`.

## Post-merge audit contract

After normal merge, the auditor must confirm:

- checked-out `HEAD`, local `main`, and `origin/main` resolve to the same merge;
- the worktree is clean;
- this complete Stage 9.2.3 closure package is present on `main`;
- service and focused-test blob identities remain unchanged;
- no production access or mutation occurred during governance closure;
- the accepted operational evidence remains preserved; and
- Stage 9.2.4 has not begun.

Successful normal merge and audit publish and activate Project Owner
acceptance, close Stage 9.2.3, and make Stage 9.2.4 eligible only for its
separate security/exclusion audit workflow.
