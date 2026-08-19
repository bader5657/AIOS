# Exact Unit Artifact Contract

The future tracked unit must contain one instance of each section and the following policy-equivalent content in this order:

```ini
[Unit]
Description=AIOS Production Telegram Application
Wants=network-online.target docker.service
After=network-online.target docker.service
StartLimitIntervalSec=300s
StartLimitBurst=5

[Service]
Type=simple
User=aiosadmin
Group=aiosadmin
WorkingDirectory=/opt/aios-src
EnvironmentFile=/opt/aios/runtime/config/runtime.env
ExecStartPre=/opt/aios/runtime/venv/bin/python -c "import os,sys; sys.exit(0 if os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('AIOS_REGISTRY_DATABASE_URL') else 1)"
ExecStart=/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main
Restart=on-failure
RestartSec=10s
TimeoutStopSec=30s
KillMode=control-group
NoNewPrivileges=true
PrivateTmp=true
UMask=0027

[Install]
WantedBy=multi-user.target
```

`StartLimitIntervalSec` and `StartLimitBurst` belong in `[Unit]` under the targeted modern systemd semantics. `UMask` is the correct systemd directive spelling. Defaults provide SIGTERM shutdown and stdout/stderr journald capture, so `KillSignal`, `StandardOutput`, and `StandardError` are intentionally omitted.
