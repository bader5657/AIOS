# Environment, Secrets, and Runtime Data

The current application loads `/opt/aios/runtime/config/runtime.env`. The future unit must consume the approved runtime environment without embedding values in the unit or repository. Whether this is expressed with systemd `EnvironmentFile=` and its exact syntax is decided in 9.1.2.

Required production variables are:

- `TELEGRAM_BOT_TOKEN`;
- `AIOS_REGISTRY_DATABASE_URL`.

`AIOS_ENV` is contextual and currently optional. `AIOS_REGISTRY_TEST_DATABASE_URL` is test-only and must never be provided as a production fallback.

Missing `TELEGRAM_BOT_TOKEN` already fails before Telegram Application construction. Invalid or missing required production configuration must fail closed; no secret/default DSN may be synthesized. Missing Registry DSN currently surfaces when the eligible Registry path constructs its dependency, not at process startup. Any new startup preflight requires separate runtime authority and is not created by this contract.

Secrets, PostgreSQL data, logs, backups, temporary downloads, manifests, and original business files remain outside Git. The service must not write runtime data into `/opt/aios-src` or any tracked source path. Exact runtime file ownership and permission modes belong to 9.1.2/9.2.3.
