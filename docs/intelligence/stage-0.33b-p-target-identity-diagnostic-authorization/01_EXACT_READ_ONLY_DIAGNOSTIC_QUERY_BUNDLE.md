# Stage 0.33B-PD Exact Read-Only Diagnostic Query Bundle

## Immediate pre-session activation gate

Immediately before production connection, require `HEAD == main == origin/main`,
a clean worktree, the exact reviewed authorization content on current `main`,
and the unchanged frozen production target and control-plane contract. Record
the reviewed PR head, authorization merge commit, and current-main commit. The
previous Stage 0.33B-P authority must remain recorded as consumed, and no newer
governance may have revoked or incompatibly superseded this authority.

Failure of any source, content, target, or control-plane check before connection
means the diagnostic authority is inactive and unconsumed: STOP without opening
PostgreSQL. Do not auto-pull, merge, rebase, reset, clean, recreate, replace,
restart, repair, fall back, or substitute an alternate target/control plane.
D01 remains the first database-side identity verification after material session
start. The authority remains exactly one future diagnostic session; it does not
authorize a full Stage 0.33B-P rerun, Migration 0005, or Migration 0004.

## Closed query surface

Only the single canonical executable bundle below is authorized. No statement
may be missing, added, duplicated, reordered, substituted, or extended. No
exploratory/ad-hoc SQL, arbitrary SELECT, additional diagnostic query, runtime
statement addition, manual catalog inspection, or query branch is authorized.

Before production connection, mechanical validation must require:

`actual_statement_sequence == frozen_statement_sequence`

The exact sequence is P01, P02, P03, P04, P05, D01, D02, C01. Validation must
reject a missing, additional, duplicate, reordered, or unknown statement; any
DDL, DML, `LOCK TABLE`, GRANT, REVOKE, COPY, DO, CALL, EXECUTE, or PREPARE; any
unapproved function; and every line beginning with optional whitespace followed
by `\`. The psql meta-command count must be zero.

## Function and client safety

The only function calls authorized are the exact frozen calls to
`current_database()`, `current_schema()`, and
`current_setting('server_version')`. Non-allowlisted, side-effecting,
user-defined, extension, advisory-lock, backend-control, file, large-object,
notification, configuration-control, or dynamic-execution functions are
prohibited.

Every psql backslash command is prohibited, including `\!`, `\copy`, `\gexec`,
`\i`, `\ir`, `\o`, and `\w`. Shell execution, file input/output, output
redirection, COPY, dynamic SQL, SQL-generating-SQL, DO, CALL, EXECUTE, PREPARE,
and `LOCK TABLE` are prohibited.

## CANONICAL EXECUTABLE TARGET-IDENTITY DIAGNOSTIC SQL BUNDLE

This is the one authoritative executable SQL bundle. All other SQL references
in this package are NON-EXECUTABLE EXPLANATION.

```sql
-- P01 BEGIN READ ONLY
BEGIN READ ONLY;

-- P02 SET LOCAL TIME ZONE
SET LOCAL TIME ZONE 'UTC';

-- P03 SET LOCAL DateStyle
SET LOCAL DateStyle = 'ISO, YMD';

-- P04 SET LOCAL IntervalStyle
SET LOCAL IntervalStyle = 'iso_8601';

-- P05 SET LOCAL bytea_output
SET LOCAL bytea_output = 'hex';

-- D01 exact target identity
SELECT
    current_database() AS database_name,
    current_user AS session_user,
    current_schema() AS schema_name,
    current_setting('server_version') AS server_version;

-- D02 exact database, schema, and relation ownership identity
SELECT
    d.datname AS database_name,
    dr.rolname AS database_owner,
    n.nspname AS schema_name,
    nr.rolname AS schema_owner,
    c.relname AS relation_name,
    c.relkind AS relation_kind,
    cr.rolname AS relation_owner
FROM pg_catalog.pg_database AS d
JOIN pg_catalog.pg_roles AS dr
  ON dr.oid = d.datdba
JOIN pg_catalog.pg_namespace AS n
  ON n.nspname = 'public'
JOIN pg_catalog.pg_roles AS nr
  ON nr.oid = n.nspowner
JOIN pg_catalog.pg_class AS c
  ON c.relnamespace = n.oid
 AND c.relname = 'material_receipts'
JOIN pg_catalog.pg_roles AS cr
  ON cr.oid = c.relowner
WHERE d.datname = current_database()
ORDER BY d.datname, n.nspname, c.relname;

-- C01 transaction close
COMMIT;
```

No other `SET` or transaction close is authorized. `COMMIT;` is harmless because
the transaction is READ ONLY and contains only the two frozen catalog/identity
SELECT statements.

## Execution and evidence contract

D01 must execute first and prove database `aios`, session user `aios`, schema
`public`, and PostgreSQL major version 17 before D02 is interpreted. A D01
mismatch is **DIAGNOSTIC BLOCKED — STOP**. The executor must not add a query to
explain it.

D02 must retain these exact bounded values without reinterpretation or
normalization:

- `database_name`;
- `database_owner`;
- `schema_name`;
- `schema_owner`;
- `relation_name`;
- `relation_kind`; and
- `relation_owner`.

Ownership values are discoveries, not D02 pass assertions. In particular,
`schema_owner != 'aios'` does not itself block the diagnostic. Structural target
failure does block: database must be `aios`, schema must be `public`, relation
must be `material_receipts`, and relation kind must be `r`, an ordinary table.
If D02 returns no exact structural target row or fails unexpectedly, the
diagnostic authority is consumed and execution returns to governance without an
additional query or rerun.

Evidence is limited to the D01/D02 identity, version, relation-kind, and owner
values. It contains no business rows, password/verifier, token, API key,
credential DSN, `DATABASE_URL`, runtime.env content, or private key.

