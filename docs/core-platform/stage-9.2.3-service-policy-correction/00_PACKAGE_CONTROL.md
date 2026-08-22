# Stage 9.2.3 Source/Runtime Separation Service Policy Correction

| Control | Value |
|---|---|
| Official stage | `Stage 9.2.3 — Establish /opt/aios-src source and /opt/aios runtime separation` |
| Exact policy-correction baseline | `86d127f94494f1c18364035480302b9751c1d534` |
| Stage 9.2.2 status | `VERIFIED — ACCEPTED — CLOSED` |
| Stage 9.2.3 evaluation status | `IDENTIFIED — READY FOR SOURCE/RUNTIME SEPARATION GOVERNANCE WORKFLOW` |
| Classification | `GOVERNANCE-ONLY SERVICE POLICY CORRECTION` |
| Service artifact effect | `NONE` |
| Test effect | `NONE` |
| VPS/runtime effect | `NONE` |
| Policy status | `PUBLISHED — ACTIVE` upon normal merge |

This package narrowly corrects the active Stage 9.1.2 systemd service policy
so a later, separately approved Stage 9.2.3 implementation can prevent normal
Python execution from generating bytecode inside `/opt/aios-src`.

The correction authorizes policy values only. It does not edit or install the
service artifact, create a runtime cache directory, change permissions, remove
existing bytecode, run tests against production, reload systemd, restart the
service, reboot, or otherwise access or mutate the VPS.

## Package index

- `01_AUTHORITY_ROOT_CAUSE_AND_CORRECTION.md`
- `02_COMPATIBILITY_AND_UNCHANGED_POLICY_MATRIX.md`
- `03_FUTURE_IMPLEMENTATION_VERIFICATION_AND_ROLLBACK.md`
- `04_BOUNDARIES_PROJECT_OWNER_APPROVAL_AND_ACTIVATION.md`
