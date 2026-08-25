# Corrected Structured Verifier Contract

## Prohibited failure path

The previous expression must not be reused:

```sql
contype || ':' || conname || ':' || pg_get_constraintdef(oid)
```

In particular, `contype || ':'` is prohibited. PostgreSQL internal catalog
`"char"` values must not rely on implicit string concatenation. Return fields
separately. Where text is required, use `c.contype::text`; for comparison, use
an explicitly typed value or compare the explicit text representation.

## Structured constraint query

The authorized constraint inspection is equivalent to:

```sql
SELECT
    c.conname,
    c.contype::text AS constraint_type,
    pg_get_constraintdef(c.oid, true) AS definition
FROM pg_constraint AS c
JOIN pg_class AS t
    ON t.oid = c.conrelid
JOIN pg_namespace AS n
    ON n.oid = t.relnamespace
WHERE t.relname = 'material_stock'
  AND n.nspname = current_schema()
ORDER BY c.conname;
```

Require exactly three checks and one primary key. Evaluate definitions
independently for semantics equivalent to `btrim(name) <> ''`,
`stock_qty >= 0`, and the exact unit set `sheet`, `pcs`, `kg`, `roll`, `pack`.
Constraint names are supporting evidence, not the sole proof of semantics.

## Columns

Use `information_schema.columns`, scoped to `current_schema()` and
`material_stock`, returning ordinal position, name, data type, UDT name,
nullability, default, precision, and scale as separate columns. Require exactly:

1. `material_id`: UUID, not null, no default;
2. `name`: text, not null, no default;
3. `stock_qty`: numeric precision 20 scale 6, not null, no default;
4. `unit`: text, not null, no default;
5. `is_active`: boolean, not null, no default;
6. `updated_at`: timestamptz, not null, no default.

## Primary key and foreign keys

Query `pg_constraint` with the same exact relation/schema scoping. Use
`c.contype::text = 'p'` or an equivalent explicitly typed comparison and column
metadata from `conkey`/`pg_attribute`. Require exactly one primary key whose sole
column is `material_id`. Do not infer correctness solely from index names.

Use `c.contype::text = 'f'` or `c.contype = 'f'::"char"` for the FK check.
Require zero foreign keys.

## Indexes, triggers, and routines

Use separate fields from `pg_index`, `pg_class`, `pg_namespace`, and
`pg_attribute`. Require exactly one table index, `indisprimary = true`, whose
sole indexed key is `material_id`; require no secondary index.

Query `pg_trigger` for the exact relation and require zero rows where
`NOT tgisinternal`.

Do not assert global absence of database functions/procedures. Establish only
that the migration created no routine attributable to `material_stock` and no
trigger-owned helper, using bounded dependency and trigger checks. The immutable
migration SQL itself contains no routine creation statement.

## State preservation

Within the transaction, require `SELECT count(*) FROM material_stock` to return
exactly zero. Do not insert test rows. Compare bounded pre/post unrelated-schema
identities and role/grant fingerprints. Require all unrelated objects present,
no role mutation, no change to grants on pre-existing tables, and no non-owner
grant on `material_stock`.
