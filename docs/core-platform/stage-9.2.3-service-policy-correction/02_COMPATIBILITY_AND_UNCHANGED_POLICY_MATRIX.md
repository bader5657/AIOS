# Compatibility and Unchanged Service Policy

## Source-write compatibility audit

The current production source was statically reviewed for runtime writes:

- Python import bytecode is the identified source write and is redirected by
  the corrected cache-prefix policy.
- original-file writes target `/opt/aios/data/documents/...`;
- Manifest creation and its atomic temporary file target
  `/opt/aios/data/documents/manifests`;
- Telegram download staging uses the operating-system temporary directory;
- `PrivateTmp=true` isolates `/tmp` and `/var/tmp` but does not hide or block
  `/opt/aios/runtime/cache/pycache`;
- systemd/journald captures stdout and stderr; no application file-log writer
  or source log path was found;
- no SQLite or other local application-state writer was found; and
- no generated application file legitimately targets `/opt/aios-src`.

After cache redirection, the service requires no write access to source.

`READONLYPATHS COMPATIBILITY = PASS`

`PRIVATETMP COMPATIBILITY = PASS`

No special read/write exception under `/opt/aios-src` is required. If future
implementation review discovers a legitimate source write, implementation
must stop with:

`STAGE 9.2.3 SOURCE WRITE CONTRACT CONFLICT`

## Unchanged Stage 9.1.2 policy matrix

| Existing policy | Corrected value |
|---|---|
| `Type` | `simple` — unchanged |
| `User` | `aiosadmin` — unchanged |
| `Group` | `aiosadmin` — unchanged |
| `WorkingDirectory` | `/opt/aios-src` — unchanged |
| `EnvironmentFile` | `/opt/aios/runtime/config/runtime.env` — unchanged |
| `ExecStartPre` | Existing exact preflight — unchanged |
| `ExecStart` | `/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main` — unchanged |
| `Restart` | `on-failure` — unchanged |
| `RestartSec` | `10s` — unchanged |
| Start limits | `300s` / `5` — unchanged |
| `TimeoutStopSec` | `30s` — unchanged |
| `KillMode` | `control-group` — unchanged |
| `NoNewPrivileges` | `true` — unchanged |
| `PrivateTmp` | `true` — unchanged |
| `UMask` | `0027` — unchanged |
| `WantedBy` | `multi-user.target` — unchanged |
| Docker/network ordering | Existing soft ordering — unchanged |
| Single-polling policy | One systemd-owned process/lifecycle — unchanged |
| Migration policy | No automatic production migration — unchanged |
| Logging/monitoring | systemd/journald only — unchanged |

The only additions are the exact `Environment=PYTHONPYCACHEPREFIX=...` and
`ReadOnlyPaths=...` directives. This package does not reopen any other settled
Stage 9.1.2 decision.
