# Schema Contract, Postflight, Evidence, and Rollback

## Exact expected table contract

The only newly created table is `material_stock`, with exactly six columns in
this order:

| Column | Exact contract |
|---|---|
| `material_id` | `UUID NOT NULL PRIMARY KEY`; no default |
| `name` | `TEXT NOT NULL`; `CHECK (btrim(name) <> '')` |
| `stock_qty` | `NUMERIC(20,6) NOT NULL`; `CHECK (stock_qty >= 0)` |
| `unit` | `TEXT NOT NULL`; exact allowed values `sheet`, `pcs`, `kg`, `roll`, `pack` |
| `is_active` | `BOOLEAN NOT NULL`; no default |
| `updated_at` | `TIMESTAMPTZ NOT NULL`; no default |

There must be no foreign key, trigger, function, secondary index beyond the
primary-key index, role/grant change, seed data, or Registry linkage.

## Mandatory post-migration verification

Before commit, use catalog/introspection and read-only queries to verify:

1. `material_stock` exists and has exactly the six expected columns and types.
2. `material_id` is the UUID primary key and has no default.
3. `name` is non-null and the blank-name check exists.
4. `stock_qty` is `NUMERIC(20,6)`, non-null, and has the nonnegative check.
5. `unit` is non-null and its constraint has exactly the five approved values.
6. `is_active` is `BOOLEAN NOT NULL` with no default.
7. `updated_at` is `TIMESTAMPTZ NOT NULL` with no default.
8. There are no foreign keys, non-internal triggers, or extra secondary indexes.
9. `SELECT count(*) FROM material_stock` returns exactly `0`.
10. No role/grant change is attributable to the migration.
11. The preflight inventory of unrelated production tables is unchanged.
12. PostgreSQL remains healthy.

Do not insert any row or test constraint behavior in production. Those behaviors
were verified in isolated integration tests. If in-transaction verification is
inconsistent, roll back. If an inconsistency is detected only after commit while
the table remains empty, stop and return to governance for a controlled rollback
decision; do not repair automatically.

## Minimum reasonable rollback posture

This is additive DDL for one empty table. A full database restore is not normally
required. Retain the exact down-migration identity:

- path: `migrations/postgres/0002_create_material_stock.down.sql`;
- SHA-256: `045dc369c3b0a7174463bdb80a9b1831666f8827a857226da52a9ec670e9b0c3`.

The down migration contains only `DROP TABLE material_stock;` and no `CASCADE`.
It may be used only under a controlled rollback decision when migration or
post-verification fails and no real material data has been inserted. Once any
real material data exists, destructive rollback requires separate authority.

## Evidence retention

Retain timestamp, production database identity, source SHA, migration path and
SHA-256, absence/collision result, preflight health, transaction result,
post-migration schema introspection, zero row count, postflight PostgreSQL
health, rollback status, and final classification. Never retain database
credentials.

Successful execution is classified
`MATERIAL_STOCK_PRODUCTION_SCHEMA_DEPLOYED`. It proves only deployment of the
empty schema; it does not prove material data, reader-role provisioning,
retrieval, or Brain stock-answer capability.
