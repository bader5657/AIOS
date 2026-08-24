# AIOS Intelligence Stage 0.21 — First Session-Bound Level B v1 Execution Approval

| Control | Approved value |
|---|---|
| Work type | `FIRST-SESSION EXECUTION APPROVAL ONLY` |
| Approval baseline | `207174b64827905cce375f876896e69dd88f2fdd` |
| Stage 0.1–0.20 | `VERIFIED — ACCEPTED — CLOSED` |
| Level B v1 activation model | `APPROVED` |
| Session harness validation | `PASS` |
| Journal root provisioning | `PASS` |
| First live session | exactly one session, exactly two fixed synthetic requests |
| General Level B ceiling | five requests or thirty minutes, unchanged |
| Production or architecture change | `NO` |
| Decision | `APPROVED AFTER GOVERNANCE ACTIVATION` |

This package grants authority for the first live Session-Bound Level B v1
staging session only. It does not execute that session. Governance publication
must not construct a composition, create a live journal, call the provider, or
send an `/api/chat` request.

After merge, synchronized clean-main audit, and fresh session preflight, the
execution authority is exactly one session containing the two requests frozen
in this package. No third request or second attempt is authorized.

The journal root is exactly:

`/opt/aios/runtime/intelligence/staging/level-b-sessions`

Its accepted identity is a real, non-symlink directory owned by
`aiosadmin:aiosadmin` with mode `0750`; its parent remains unchanged.

