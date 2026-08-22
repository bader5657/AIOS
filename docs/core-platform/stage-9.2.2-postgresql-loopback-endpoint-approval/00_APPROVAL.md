# Stage 9.2.2 PostgreSQL Loopback Endpoint Approval

- Classification: `CONTROLLED PRODUCTION ENDPOINT AND CONFIG RECONCILIATION`
- VPS: `aiosadmin@aios-prod-01`
- Compose path: `/opt/aios/docker/postgres/compose.yml`
- Compose service: `postgres`
- Container: `aios-postgres`
- Exact publication: `127.0.0.1:5432:5432/tcp`
- Data bind mount: `/opt/aios/docker/postgres/data:/var/lib/postgresql/data`
- Follow-on config: `/opt/aios/runtime/config/runtime.env`
- Approval status: `PUBLISHED — ACTIVE` upon normal merge

Authority permits only adding the exact loopback port mapping to the existing
PostgreSQL service, validating the resulting Compose config, and recreating
only that service with its existing environment, bind mount, network, restart
policy, and healthcheck unchanged. `docker compose down`, volume removal,
credential changes, database/user creation, migrations, and schema/data writes
are prohibited. Rollback restores the protected pre-change Compose file and
recreates only the PostgreSQL service with the same data bind mount.

After the container is healthy, authority permits host-level read-only
`SELECT 1` through `127.0.0.1:5432`, followed by the already-scoped production
configuration reconciliation: preserve a protected `runtime.env` backup, add
or replace only one `AIOS_REGISTRY_DATABASE_URL` using the existing Compose
credential source, keep `TELEGRAM_BOT_TOKEN` unchanged, keep
`AIOS_REGISTRY_TEST_DATABASE_URL` absent, and set `root:aiosadmin 0640`.
Credential values and the complete DSN must never be logged.

The active predecessor `aios.service` must not be stopped, restarted, reloaded,
or replaced. Application source, both virtual environments, Storage, unrelated
containers, and Stage 9.2.3 are outside authority. A temporary PostgreSQL
interruption during the single-service recreate does not authorize AIOS
restart or another poller.

I, as Project Owner, approve this narrow Stage 9.2.2 PostgreSQL endpoint
reconciliation. The existing PostgreSQL service may be published to the VPS
host only at `127.0.0.1:5432/tcp` for the host-level AIOS service. It must not
be publicly exposed. No database schema, data, credential, volume, migration,
or application semantic change is authorized. After endpoint verification,
the production Registry DSN may be added using the approved configuration
procedure above.

`STAGE 9.2.2 POSTGRESQL LOOPBACK ENDPOINT APPROVED — READY FOR CONTROLLED EXECUTION`
