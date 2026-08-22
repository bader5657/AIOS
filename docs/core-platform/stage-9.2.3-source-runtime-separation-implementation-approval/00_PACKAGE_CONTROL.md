# Stage 9.2.3 Source/Runtime Separation Implementation Approval

| Control | Value |
|---|---|
| Official stage | `Stage 9.2.3 — Establish /opt/aios-src source and /opt/aios runtime separation` |
| Exact implementation-approval baseline | `9da47009e7f7b92f1022c6daf2b4393fd48d7263` |
| Stage 9.2.2 status | `VERIFIED — ACCEPTED — CLOSED` |
| Service-policy correction | `ACTIVE — READY FOR IMPLEMENTATION APPROVAL` |
| Classification | `GOVERNANCE / REPOSITORY IMPLEMENTATION APPROVAL ONLY` |
| Authorized repository paths | `2` |
| Service, test, or runtime effect | `NONE` |
| VPS/production effect | `NONE` |
| Approval status | `PUBLISHED — ACTIVE` upon normal merge |

This package authorizes a future repository implementation of the two exact
active Stage 9.2.3 policy directives and durable focused tests. It does not
perform that implementation, edit tests, access production, create runtime
paths, install a unit, reload systemd, restart the service, or reboot.

## Package index

- `01_AUTHORITY_AND_EXACT_AUTHORIZED_SCOPE.md`
- `02_SYSTEMD_AND_PYTHON_SEMANTICS.md`
- `03_TEST_AND_VERIFICATION_CONTRACT.md`
- `04_PRODUCTION_BOUNDARY_ROLLBACK_AND_STAGE_LIMITS.md`
- `05_PROJECT_OWNER_APPROVAL_PUBLICATION_AND_ACTIVATION.md`
