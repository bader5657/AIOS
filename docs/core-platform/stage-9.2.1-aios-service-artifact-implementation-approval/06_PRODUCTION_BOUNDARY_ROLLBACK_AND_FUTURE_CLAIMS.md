# Production Boundary, Rollback, and Future Claims

Stage 9.2.1 creates only reviewed repository artifacts. Installation to `/etc/systemd/system/aios.service`, daemon-reload, enable/start/restart, systemctl/journalctl, Telegram polling, production database access, permission changes, and VPS execution remain prohibited until Stage 9.2.2 authority.

The artifact must not claim that it is installed, enabled, active, reboot-verified, single-polling-verified, database-connected, Storage-writable, or journal-verified. Those are Stage 9.2.2 evidence.

Repository rollback is limited to reverting/removing the two new tracked implementation paths. There is no operational or data rollback because Stage 9.2.1 performs no installation. PostgreSQL data, originals, Metadata, Manifests, Registry rows, Events, and Core results are never rollback targets.
