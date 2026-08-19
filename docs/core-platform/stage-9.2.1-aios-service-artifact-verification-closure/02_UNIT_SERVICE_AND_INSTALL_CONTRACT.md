# Unit, Service, and Install Contract Evidence

The tracked unit contains the exact approved sections and directives.

## Unit

- `Description=AIOS Production Telegram Application`
- `Wants=network-online.target docker.service`
- `After=network-online.target docker.service`
- `StartLimitIntervalSec=300s`
- `StartLimitBurst=5`

There is no hard `Requires=docker.service` relationship. Network and Docker are
soft ordering dependencies only.

## Service

- `Type=simple`
- `User=aiosadmin`
- `Group=aiosadmin`
- `WorkingDirectory=/opt/aios-src`
- `EnvironmentFile=/opt/aios/runtime/config/runtime.env`
- exactly one interpreter-only `ExecStartPre`
- `ExecStart=/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`
- `Restart=on-failure`
- `RestartSec=10s`
- `TimeoutStopSec=30s`
- `KillMode=control-group`
- `NoNewPrivileges=true`
- `PrivateTmp=true`
- `UMask=0027`

The environment file is mandatory: its path has no optional `-` prefix. There
is exactly one `ExecStart`, preserving one service, one foreground Python
process, and one Telegram Adapter `run_polling()` lifecycle. `Restart` is
process recovery and does not introduce pipeline or business retry.

## Install

- `WantedBy=multi-user.target`

This install declaration supports later enablement, but does not prove that the
service is installed, enabled, or active.
