# Preflight, Entrypoint, and Single-Polling Review

From `WorkingDirectory=/opt/aios-src`, the runtime interpreter can import `core.adapters.telegram.main` through normal module execution; no `PYTHONPATH`, wrapper, shell, or Python change is authorized.

The exact interpreter-only `ExecStartPre` is required by Stage 9.1.2. It checks only that `TELEGRAM_BOT_TOKEN` and `AIOS_REGISTRY_DATABASE_URL` are non-empty, prints no secret, connects to no network/database, performs no migration, and introduces no helper artifact.

The unit has exactly one `ExecStart` and one foreground process. It contains no worker fan-out, second poller, PID/file lock, retry loop, alternate supervisor, application container, or manual launcher. `Restart=on-failure` is process recovery only and does not alter pipeline/business retry `NONE`.
