# Service, Database, Storage, and Journal Invariants

## Service and single-poller evidence

| Check | Accepted result |
|---|---|
| Unit | `aios.service` |
| Active | `YES` |
| Enabled | `YES` |
| MainPID | `15845` |
| NRestarts | `0` |
| Telegram polling processes | exactly `1` |
| Active interpreter | `/opt/aios/runtime/venv/bin/python` |
| Crash/restart loop | `NONE OBSERVED` |
| Telegram polling conflict | `NONE OBSERVED` |

## PostgreSQL invariant

- Container: `aios-postgres`
- Health: `HEALTHY`
- Endpoint: `127.0.0.1:5432`
- Public exposure: `NONE`
- Migration: `NONE`
- Database mutation: `NONE`
- Schema mutation: `NONE`

## Storage and configuration invariants

- Storage read: `PASS`
- Storage write: `PASS`
- Storage path/data/ownership/mode change: `NONE`
- `runtime.env` mutation: `NONE`
- Python/application semantic change: `NONE`
- Registry/Event/Core/business semantic change: `NONE`

## Journal and safety evidence

The current Stage 9.2.3 startup is visible through journald. No crash loop,
pycache permission error, source read-only error, Telegram conflict, or secret
leakage was observed.

No reboot was performed or required. Stage 9.2.2 reboot evidence remains
authoritative. No VPS access or mutation is performed by this governance-only
closure.
