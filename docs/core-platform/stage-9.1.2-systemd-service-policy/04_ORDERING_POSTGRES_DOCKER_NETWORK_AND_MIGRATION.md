# Ordering, PostgreSQL, Docker, Network, and Migration

The minimal future Unit ordering policy is:

- `Wants=network-online.target docker.service`
- `After=network-online.target docker.service`

Neither `Requires=docker.service` nor a PostgreSQL container unit dependency is approved. These soft dependencies request and order basic network/Docker availability without making `aios.service` own Docker Compose or the PostgreSQL container.

No database connectivity preflight is required at service start. With a valid DSN, Registry operations retain their existing fail-closed behavior when PostgreSQL is unavailable. Stage 9.2.2 must separately verify expected PostgreSQL interaction.

`AUTOMATIC PRODUCTION MIGRATION ON AIOS SERVICE START = PROHIBITED`.

Migration execution remains operator-controlled under separate production authority. The unit must not apply UP/DOWN migrations or invoke a migration framework.
