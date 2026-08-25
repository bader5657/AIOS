# Root Cause and Corrected Verification Contract

## Exact root cause

The failing expression was:

```sql
contype || ':' || conname || ':' || pg_get_constraintdef(oid)
```

The failure began at `contype || ':'`. `pg_constraint.contype` uses PostgreSQL's
internal catalog type `"char"`. Combining it with the untyped string literal
through `||` left PostgreSQL with no unique concatenation operator, producing:

```text
ERROR: operator is not unique: "char" || unknown
```

The verifier must not rely on implicit conversion of internal catalog `"char"`
values. When text is necessary, cast explicitly with `contype::text`. Structured
result columns are preferred over synthetic concatenated descriptions.

## Constraint verification

The future verifier must return constraints as structured fields:

```sql
SELECT
    c.conname,
    c.contype::text AS constraint_type,
    pg_get_constraintdef(c.oid, true) AS definition
FROM pg_constraint AS c
JOIN pg_class AS t ON t.oid = c.conrelid
JOIN pg_namespace AS n ON n.oid = t.relnamespace
WHERE t.relname = 'material_stock'
  AND n.nspname = current_schema()
ORDER BY c.contype::text, c.conname;
```

Expected rows are exactly three check constraints and one primary-key
constraint. The definitions must independently establish the nonblank `name`,
nonnegative `stock_qty`, exact five-value `unit` vocabulary, and primary key on
`material_id`.

## Column verification

Query `information_schema.columns` by schema and table, returning separate
fields for ordinal position, column name, data type, UDT name, nullability,
default, numeric precision, and numeric scale. Require exactly six ordered
columns and the approved contract. Do not combine catalog values merely for
display, and do not insert rows to test constraints.

## Primary key and foreign keys

Use `pg_constraint` scoped through `pg_class` and `pg_namespace`. Compare the
typed catalog field (`c.contype = 'p'::"char"` and `c.contype = 'f'::"char"`) or
compare `c.contype::text` to `p` and `f`. Verify the PK column through
`conkey`/attribute metadata or the structured constraint definition; do not
infer the PK solely from an index name. Require exactly one PK on
`material_id` and zero FKs.

## Indexes and triggers

Use `pg_index`, `pg_class`, `pg_namespace`, and attribute metadata as separate
fields. Require exactly one index, with `indisprimary` true and its indexed
attribute exactly `material_id`; require zero non-primary indexes.

Query `pg_trigger` for the exact table and require zero rows where
`NOT tgisinternal`.

## Functions and procedures

Do not claim global absence. The migration SQL contains no function or procedure
creation. The future verifier must establish that no routine is attributable to
`material_stock`, using bounded dependency/catalog checks where applicable,
rather than asserting that the production database has no routines.

## Remaining transaction checks

Before commit, also require table existence, row count exactly zero, unchanged
unrelated table identities, unchanged role fingerprint, unchanged grants on
pre-existing tables, and no non-owner grant on `material_stock`. PostgreSQL must
remain healthy. All verification is read-only and occurs without production
constraint `INSERT` tests.
