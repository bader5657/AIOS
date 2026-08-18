# Database and Production Audit

Database evidence used only `AIOS_REGISTRY_TEST_DATABASE_URL` against the
existing disposable PostgreSQL service. Tests created unique schemas, applied
the existing unchanged migration, and dropped schemas during cleanup.

`AIOS_REGISTRY_DATABASE_URL` was removed from test process environments.
Production database access, credentials, fallback, migration, and mutation were
prohibited and did not occur.
