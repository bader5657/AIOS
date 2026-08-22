# Stage 9 Exit Criteria Matrix

| # | Exit criterion | Result | Principal evidence |
|---:|---|---|---|
| 1 | All numbered Stage 9 work closed | `PASS` | 9.1.1–9.3.1 ledger; `7/7 CLOSED` |
| 2 | Authoritative service contract exists | `PASS` | Stage 9.1.1/9.1.2 authority and Stage 9.2.1 artifact closure |
| 3 | Production service operational | `PASS` | enabled, active, non-root, approved venv and config |
| 4 | Reboot lifecycle verified | `PASS` | controlled reboot and automatic activation evidence |
| 5 | Exactly one production poller | `PASS` | `1 → 0 → 1`; no concurrent/alternate poller |
| 6 | Source/runtime separation verified | `PASS` | read-only source, external cache, clean runtime operation |
| 7 | Security/exclusion verified | `PASS` | Stage 9.2.4 eleven-category conformance |
| 8 | PostgreSQL operational boundary verified | `PASS` | healthy, loopback-only, external persistent data, DSN/connectivity evidence |
| 9 | Observability surfaces verified | `PASS` | systemctl and journald evidence |
| 10 | Later-phase capability exclusion preserved | `PASS` | Brain/Intelligence/Memory/Specialist/business/automation absent |
| 11 | Capability claims reconciled | `PASS` | Stage 9.3.1 final closure |
| 12 | Zero blocking defects | `PASS` | accepted evaluation and deferred-item disposition |

`STAGE 9 EXIT CRITERIA = 12/12 PASS`

`STAGE 9 EXIT GATE RESULT = ELIGIBLE_WITH_ACCEPTED_DEFERRED_ITEMS`

Remaining blockers: `NONE`.
