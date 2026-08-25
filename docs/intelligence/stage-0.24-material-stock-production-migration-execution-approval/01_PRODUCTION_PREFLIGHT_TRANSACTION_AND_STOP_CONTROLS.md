# Production Preflight, Transaction, and Stop Controls

## Mandatory source preflight

Immediately before any production database connection or execution, retain:

- UTC timestamp;
- proof that `HEAD == main == origin/main` after refreshing the remote ref;
- proof that the worktree is clean;
- exact path `migrations/postgres/0002_create_material_stock.up.sql`;
- exact SHA-256
  `a6d4a7be98fe8ecb6914a6231f9d2ddcd76e2ec7fb30a87759d8ba6be9320d5f`.

Any mismatch is `PRODUCTION_MIGRATION_PREFLIGHT_BLOCKED`. Stop and return to
governance.

## Mandatory PostgreSQL preflight

Using read-only inspection, record the exact production server, database, user,
and schema identity without retaining credentials. Confirm:

- the intended production PostgreSQL container/service is healthy;
- connection to the recorded database succeeds;
- the database identity is production and not an isolated or test database;
- a harmless explicit transaction can begin and roll back;
- unrelated production tables are inventoried sufficiently to prove they remain
  intact after execution;
- `to_regclass('material_stock') IS NULL` in the target resolution context;
- no production migration-history entry collides with
  `0002_create_material_stock`, if a production history mechanism exists.

Repository inspection found no persistent migration-history mechanism. If the
production environment independently has one, inspect it read-only. Do not
create or modify migration history in this stage.

If `material_stock` exists, an identifier collides, health or identity is
uncertain, transaction capability fails, or any preflight is incomplete: stop
with `PRODUCTION_MIGRATION_PREFLIGHT_BLOCKED`. Do not drop, alter, overwrite,
repair, or continue.

## Execution authority

Exactly one SQL execution attempt is authorized after all gates pass. Preflight
queries do not consume the attempt. There is no automatic or manual retry under
this authority after a failed execution attempt.

Execute the exact verified up-migration in one explicit PostgreSQL transaction:

1. `BEGIN`.
2. Execute the immutable up-migration exactly once.
3. Perform the in-transaction read-only schema and zero-row verification.
4. `COMMIT` only if every verification passes.

If the migration SQL fails, issue `ROLLBACK`, stop, retain evidence, and classify
`PRODUCTION_MIGRATION_FAILED_ROLLED_BACK`. Do not continue after partial failure
and do not improvise schema repair.

No statement outside the exact migration and the required transaction/read-only
verification is authorized. In particular: no insert, constraint probe, role,
grant, seed, Registry linkage, unrelated DDL, or service/runtime action.
