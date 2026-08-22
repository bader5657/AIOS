# Production Isolation and Non-Execution

## Unloaded and unexecuted state

Read-only `ollama list` shows the approved Qwen model present. Read-only
`ollama ps` returns an empty model table. The complete staging-container log
contains health, list, process-state, and the original acquisition requests
only: `HEAD /`, `GET /api/version`, `GET /api/ps`, `GET /api/tags`, and
`POST /api/pull`.

There is no generate, chat, embeddings, or runner-load request in the log.
Therefore:

- model present: `YES`;
- model loaded: `NO`;
- inference executed: `NO`;
- benchmark executed: `NO`.

## Protected production state

| Protected component | Current evidence | Result |
|---|---|---|
| `aios.service` | `active/running`; `MainPID=15845`; `NRestarts=0` | `PASS` |
| PostgreSQL | `aios-postgres` healthy; `127.0.0.1:5432` only | `PASS` |
| Telegram | exactly one poller process, PID `15845`, `python -m core.adapters.telegram.main` | `PASS` |
| Core/Brain integration | no Ollama/Qwen production wiring authorized | `NONE` |
| Production inference authority | not granted | `NONE` |

The production Docker daemon and isolated staging daemon remain distinct. This
verification did not install, download, restart, benchmark, execute inference,
or change any container, network, firewall rule, service, source, secret,
volume, model, or runtime configuration.
