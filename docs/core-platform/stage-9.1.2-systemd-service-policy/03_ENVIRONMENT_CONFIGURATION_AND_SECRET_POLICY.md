# Environment, Configuration, and Secret Policy

The exact future declaration is:

`EnvironmentFile=/opt/aios/runtime/config/runtime.env`

The file is required; optional `-` semantics are prohibited. Expected ownership is `root:aiosadmin` with mode `0640`: authorized operators may write it, the service group may read it, and world access is denied. Secrets must not appear in the unit, repository, command line, or journal output.

Required production variables:

- `TELEGRAM_BOT_TOKEN`
- `AIOS_REGISTRY_DATABASE_URL`

`AIOS_ENV` is optional operational context. `AIOS_REGISTRY_TEST_DATABASE_URL` is prohibited from the production service environment and may never fall back to or replace the production DSN.

The exact local validation command is:

`ExecStartPre=/opt/aios/runtime/venv/bin/python -c "import os,sys; sys.exit(0 if os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('AIOS_REGISTRY_DATABASE_URL') else 1)"`

It performs no network or database connection and prints no secret. Missing/invalid configuration fails startup. Operator recovery is: correct the runtime environment, reset a rate-limited failed state if necessary, then explicitly restart under operational authority.
