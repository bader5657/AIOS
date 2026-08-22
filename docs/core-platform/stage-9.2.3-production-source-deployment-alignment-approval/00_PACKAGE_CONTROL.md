# Stage 9.2.3 Production Source Deployment Alignment Approval

| Control | Value |
|---|---|
| Classification | `STAGE 9.2.3 DEPLOYMENT ARTIFACT MISMATCH` |
| Governance baseline | `fe1b748ee48dddd6f01e45214e1f9a23d9724267` |
| Current VPS source | `4168e098612c930215a49028d4ca9fc200d21cfd` |
| Exact deployment target | `2c44dc84cb38dc51778f8a65f12a6e59683c74c9` |
| Approved service blob | `8794ee77cea44dae5bb7f96d876d3a240b5a78ed` |
| Approved service SHA-256 | `02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281` |
| Approval status | `PUBLISHED — ACTIVE` upon normal merge |

This governance-only correction approves the smallest source-deployment
alignment needed before the existing Stage 9.2.3 VPS separation execution may
resume. It does not connect to or mutate the VPS, source checkout, service,
database, configuration, Docker, Storage, or business data.

## Package index

- `01_TARGET_AUTHORITY_AND_ARTIFACT_PROOF.md`
- `02_PREPARATION_AND_ROLLBACK_EVIDENCE.md`
- `03_ZERO_POLLER_SWITCH_AND_INTEGRITY_GATES.md`
- `04_EXISTING_APPROVAL_RELATION_AND_ROLLBACK.md`
- `05_PROJECT_OWNER_APPROVAL_PUBLICATION_AND_ACTIVATION.md`
