# PostgreSQL, Migration, Docker, and Network Boundaries

PostgreSQL remains a separate Docker Compose service with its existing local healthcheck and restart policy. AIOS remains a host-level systemd process; no AIOS Dockerfile or application container is required.

`aios.service` must not silently acquire ownership of Docker Compose, PostgreSQL startup, schema, data, backups, or migrations. Service ordering against `docker.service`, a database preflight, or fail-closed application behavior are unresolved alternatives for 9.1.2. No hard PostgreSQL container dependency is inferred here.

`AIOS SERVICE START MUST NOT IMPLY AUTOMATIC DATABASE MIGRATION`.

Production migrations remain operator-controlled and require separate explicit production authority. Exact migration procedure and rollback are unresolved; no Alembic or other framework is introduced.

Telegram polling requires external network availability. Whether the future unit declares `After=network-online.target`, `Wants=network-online.target`, Docker ordering, or no explicit dependency is a 9.1.2 decision based on minimum necessary ordering. Stage 9.1.1 does not select directives.
