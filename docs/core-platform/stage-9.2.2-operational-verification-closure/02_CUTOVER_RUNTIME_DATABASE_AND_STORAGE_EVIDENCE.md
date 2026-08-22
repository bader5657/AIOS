# Cutover, Runtime, Database, and Storage Evidence

## Predecessor and rollback

Before cutover there was exactly one predecessor Telegram poller. The
predecessor service stopped cleanly, the polling count reached zero, and only
then was the approved Stage 9 service started. There was no predecessor poller
and no alternate poller after cutover.

The predecessor unit artifact remains preserved at:

`/opt/aios/runtime/rollback/stage-9.2.2/service-cutover/aios.service.predecessor`

This is retained rollback evidence; closure neither consumes nor modifies it.

## Runtime and configuration reconciliation

- Active interpreter: `/opt/aios/runtime/venv/bin/python`
- Active command:
  `/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`
- Production environment: `/opt/aios/runtime/config/runtime.env`
- Environment protection: owner/group `root:aiosadmin`, mode `0640`
- `TELEGRAM_BOT_TOKEN`: `PRESENT_NONEMPTY`
- `AIOS_REGISTRY_DATABASE_URL`: `PRESENT_NONEMPTY`
- `AIOS_REGISTRY_TEST_DATABASE_URL`: `ABSENT`

Only presence/absence and protection were recorded. No token, password,
complete DSN, or environment content was disclosed.

The active interpreter proves reconciliation to the approved Stage 9 runtime
venv. The predecessor runtime did not remain active after cutover.

## PostgreSQL reconciliation

- Container: `aios-postgres`
- State after controlled reboot: `healthy`
- Host endpoint: `127.0.0.1:5432`
- Public listener/exposure: `NONE`
- Production Registry DSN: present, nonempty, and reconciled to the approved
  loopback endpoint without recording its credential-bearing value
- Preserved data: `PASS`
- Migration: `NONE`
- Schema mutation: `NONE`
- Data mutation: `NONE`

The PostgreSQL endpoint is host-loopback-only and satisfies the Stage 9.1.1
and Stage 9.1.2 network boundary. Verification did not create a database,
change credentials, migrate schema, or mutate application data.

## Storage

- Read access: `PASS`
- Write access: `PASS`

The Storage check established operational access through the approved runtime.
It introduced no Storage architecture, ownership, or semantic change.

## Cutover result

The verified single-polling transition was exactly `1 → 0 → 1`:

1. one predecessor poller;
2. clean predecessor stop and proven zero-poller gate;
3. one Stage 9 systemd-owned poller.

The initial Stage 9 service start passed. A subsequent clean stop/start of the
new service passed without duplication, conflict, or restart loop.
