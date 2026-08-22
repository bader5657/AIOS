# Runtime, Service, Privacy, and Non-Mutation Evidence

## Final observed production state

| Evidence | Result |
|---|---|
| VPS | `aios-prod-01` |
| Operator/channel | `aiosadmin` through approved `Bagus-PC` channel |
| Service | `active`; `enabled` |
| MainPID | `15845` |
| NRestarts | `0` |
| Telegram pollers | exactly `1` |
| Active interpreter | `/opt/aios/runtime/venv/bin/python` |
| Source root | `/opt/aios-src` |
| Source HEAD | `2c44dc84cb38dc51778f8a65f12a6e59683c74c9` |
| Source status | clean |
| Protected source file scan | none found |
| PostgreSQL | healthy |
| Production mutation during audit | `NONE` |

The final no-mutation check reconfirmed the same PID, restart count, single
poller, source HEAD, and clean source status. No restart, reload, service
change, source change, database/schema change, Storage change, chmod/chown,
credential change, or other production mutation was performed.

## Structural separation

- `/opt/aios/runtime` outside `/opt/aios-src`: `PASS`
- `/opt/aios/data` outside `/opt/aios-src`: `PASS`
- `/opt/aios/docker` outside `/opt/aios-src`: `PASS`

## Journal privacy classification

- `CONTEXTUAL_TELEGRAM_METADATA=PRESENT`
- `AUTHENTICATION_SECRET_PATTERN=ABSENT`
- `MATCHED_VALUES_DISCLOSED=NO`

Decision: `DOCUMENTED PRIVACY HARDENING DEFERRED`.

Contextual Telegram metadata remains a future privacy/logging-hardening item.
It is not an authentication-secret exposure and Stage 9.2.4 does not redesign
logging.
