# Stage 9.2.3 Controlled VPS Source/Runtime Separation Approval

| Control | Value |
|---|---|
| Official action | `Stage 9.2.3 Controlled VPS Source/Runtime Separation Application and Verification` |
| Exact operational baseline | `9579083000a675a264ce482eaf7323df5840e111` |
| Repository implementation | `VERIFIED — ACCEPTED — CLOSED` |
| Classification | `CONTROLLED PRODUCTION SOURCE/RUNTIME SEPARATION` |
| VPS | `aios-prod-01` |
| Service artifact | `deploy/systemd/aios.service` |
| Service Git blob | `8794ee77cea44dae5bb7f96d876d3a240b5a78ed` |
| Service SHA-256 | `02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281` |
| Approval status | `PUBLISHED — ACTIVE` upon normal merge |

This governance package authorizes one tightly controlled production
application and verification cycle only after normal merge activates the
approval. It performs no VPS connection, preflight, filesystem mutation,
systemd action, service lifecycle action, polling transition, or reboot.

The controlled executor must remain within the exact sequence, stop rules,
paths, integrity values, invariants, and rollback contract in this package.
Passing repository verification does not substitute for production preflight
or operational verification.

## Package index

- `01_AUTHORITY_TARGET_OPERATOR_AND_PREFLIGHT.md`
- `02_CACHE_ROLLBACK_AND_BYTECODE_DISPOSITION.md`
- `03_SINGLE_POLLER_INSTALLATION_AND_EFFECTIVE_UNIT.md`
- `04_SEPARATION_INVARIANTS_SUCCESS_AND_ROLLBACK.md`
- `05_BOUNDARIES_PROJECT_OWNER_APPROVAL_AND_ACTIVATION.md`
