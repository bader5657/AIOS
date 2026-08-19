# Read-Only Preflight and Safety

Before any mutation, the executor must record read-only evidence for:

- hostname, current administrative identity, OS, and systemd availability;
- Docker availability and current PostgreSQL container/service health;
- any existing `/etc/systemd/system/aios.service` and other AIOS units;
- all AIOS, Telegram module, container, supervisor, and manual polling processes;
- existence of `/opt/aios-src`, `/opt/aios`, runtime virtualenv,
  `runtime.env`, and approved Storage directories;
- `/opt/aios-src` remote, revision, branch/deployment state, and relevant files;
- executable access to `/opt/aios/runtime/venv/bin/python` by `aiosadmin`;
- importability of the AIOS entrypoint, Telegram package, psycopg, and current
  dependencies without starting the application.

If an installed unit already exists, it must be compared byte-for-byte or
semantically with the artifact whose Git blob hash is
`ace763735417d196f3841fb526d76b4e593fbbc3`. It may be classified only as exact
match, stale approved predecessor, or unauthorized/conflicting. A conflict is a
hard stop; no blind overwrite is allowed.

`COMPETING POLLING PROCESSES = ZERO` is mandatory before installation or
activation. The audit includes systemd, direct Python invocation, containers,
and alternate supervisors.

Configuration inspection is metadata- and name-only: verify owner, group,
mode, readability by `aiosadmin`, non-world-readability, non-empty
`TELEGRAM_BOT_TOKEN` and `AIOS_REGISTRY_DATABASE_URL`, and absence of
`AIOS_REGISTRY_TEST_DATABASE_URL`, without displaying values.

Storage verification may create one harmless probe only in an approved runtime
test/temp location and must remove it immediately. It must not touch business
files. PostgreSQL verification is limited to health plus a read-only
connectivity query such as `SELECT 1`; migrations and schema/data mutations are
prohibited.
