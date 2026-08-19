# Authority and Exact Artifact Paths

The active Stage 9.1.1 contract fixes one host-level service, one Python process, one Telegram polling lifecycle, separate PostgreSQL Docker Compose, systemd lifecycle ownership, source/runtime separation, runtime-only secrets, no startup migration, systemctl/journalctl observability, and no later-phase behavior.

The exact future paths are:

- tracked unit: `deploy/systemd/aios.service`;
- installed unit: `/etc/systemd/system/aios.service`.

Only one tracked and one installed authoritative copy are permitted. The tracked artifact is reviewed source; the installed artifact is operator-managed deployment state. Stage 9.2.1 requires a separate exact-path implementation approval before either exists.
