# Preflight, Operational Boundaries, and Exclusions

The single `ExecStartPre` uses
`/opt/aios/runtime/venv/bin/python -c` directly. It reads the environment loaded
from the required EnvironmentFile and exits non-zero unless both
`TELEGRAM_BOT_TOKEN` and `AIOS_REGISTRY_DATABASE_URL` are present and non-empty.

The preflight:

- invokes no shell and uses no helper artifact;
- prints no secret value;
- performs no Telegram or other network access;
- performs no database connection;
- executes no Docker or Docker Compose command;
- runs no migration or schema command.

The unit embeds no bot token, password, DSN, or API key. It does not reference
`AIOS_REGISTRY_TEST_DATABASE_URL`. Production configuration remains outside
Git at `/opt/aios/runtime/config/runtime.env`.

PostgreSQL lifecycle remains owned by its separate Docker Compose deployment.
The AIOS unit neither starts nor manages PostgreSQL. Automatic production
migration at application startup remains prohibited. No retry loop, wrapper,
worker pool, alternate supervisor, service template, lock helper, second
poller, application container, HTTP health endpoint, monitoring stack, or file
logging was introduced. Default stdout/stderr journal capture remains the
logging model.

The unit preserves source/runtime separation: code is read from
`/opt/aios-src`, while interpreter and configuration paths remain under
`/opt/aios`. Runtime semantics and Stage 8 pipeline contracts are unchanged.
