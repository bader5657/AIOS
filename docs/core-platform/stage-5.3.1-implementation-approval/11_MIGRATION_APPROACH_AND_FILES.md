# Migration Approach and Exact Files

Plain, versioned SQL is approved under the new non-conflicting directory
`migrations/postgres/`.

Exact files:

- `migrations/postgres/0001_create_registry_records.up.sql`;
- `migrations/postgres/0001_create_registry_records.down.sql`.

The up migration creates only the approved table and constraints. The down
migration reverses only the initial table creation and must include an explicit
comment warning that destructive production execution is unauthorized.

There is no runner, ledger table, framework, or bootstrap file. Ordering is by
the versioned filename only.
