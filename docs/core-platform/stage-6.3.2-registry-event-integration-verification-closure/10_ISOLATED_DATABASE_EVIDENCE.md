# Isolated PostgreSQL Evidence

Both implementation and post-merge verification used only
`AIOS_REGISTRY_TEST_DATABASE_URL` against disposable PostgreSQL schemas with
unique names. The existing migration
`migrations/postgres/0001_create_registry_records.up.sql` was applied unchanged,
and each schema was dropped during test cleanup.

The production `AIOS_REGISTRY_DATABASE_URL` was removed from each integration
test process environment. No production fallback, credentials, connection, or
mutation occurred.
