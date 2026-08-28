# Stage 0.33B-P Read-Only Query and Evidence Contract

## Closed exact governed statement model

Stage 0.33B-P uses only the **EXACT GOVERNED PREFLIGHT QUERY BUNDLE** frozen in
this document: the literal prefix, exact ordered queries, and the one harmless close
(`COMMIT;`). No SQL may be invented, extended, substituted,
reordered, or added interactively.

Exploratory or diagnostic ad-hoc SQL, “one more query,” manual inspection,
interactive troubleshooting, query substitutions, arbitrary WHERE clauses,
arbitrary SELECT expressions, arbitrary functions, and arbitrary catalog joins
are prohibited. If the bundle cannot prove a fact: INCONCLUSIVE, STOP, and do
not expand the surface.

Exact SQL order is: prefix; target identity; Migration 0005 absence; Stage 0.32
index; zero-row count; four fingerprints; structural/schema/object snapshot;
role/membership/ACL snapshot; transaction close. Separately governed non-SQL
health evidence and the secret scan/classification do not alter that SQL order.

### Function allowlist and SELECT safety

Only calls appearing in the exact queries with their frozen arguments are
allowed: `current_database()`, `current_schema()`,
`current_setting('server_version')`, `COUNT(*)`, `md5(text)`, `COALESCE`,
`string_agg`, `row_to_json`, `pg_catalog.format_type`, `pg_catalog.pg_get_expr`,
`pg_catalog.pg_get_constraintdef`, `pg_catalog.pg_get_indexdef`,
`pg_catalog.pg_get_triggerdef`, and `pg_catalog.pg_get_functiondef` solely for
four-table trigger metadata. No unlisted function is authorized.

A SELECT containing any non-allowlisted function is prohibited, including all
advisory lock/try-lock/unlock families; `set_config`; `nextval`; `setval`;
`pg_notify`; configuration/log/WAL/restore-point control; backend
cancel/terminate; large-object import/export; server-file reads/listing;
dblink/foreign execution; user-defined functions; non-allowlisted VOLATILE or
side-effecting extension functions; and procedures. This expressly includes
the `pg_advisory_*`, `pg_try_advisory_*`, `pg_reload_conf`,
`pg_rotate_logfile`, `pg_switch_wal`, `pg_create_restore_point`,
`pg_cancel_backend`, `pg_terminate_backend`, `lo_import`, `lo_export`,
`pg_read_file`, `pg_read_binary_file`, `pg_ls_dir`, and `pg_stat_file` families.

No `SELECT public.some_function`, CALL, DO/anonymous PL/pgSQL, EXECUTE, PREPARE,
format-generated execution, SQL-generating-SQL, or conditional SQL is allowed.

### Complete psql meta-command and escape ban

Stdin contains SQL only. Every line beginning with optional whitespace then `\`
is prohibited; meta-command count is zero. This bans `\!`, `\copy`, `\gexec`,
`\i`, `\ir`, `\include`, `\include_relative`, `\o`, `\out`, `\w`, `\write`,
`\watch`, `\set`, `\unset`, `\prompt`, `\password`, `\connect`, `\c`,
`\encoding`, `\edit`, `\e`, `\ef`, `\ev`, `\lo_export`, `\lo_import`,
`\lo_list`, `\shell`, `\if`, `\elif`, `\else`, and every equivalent/unknown
backslash command. The SQL string `E'\n'` is not line-leading meta syntax.

Shell execution, client/server file input, file output, program execution, COPY
or COPY PROGRAM, output redirection, result-file output, and editor invocation
are prohibited. Evidence returns only through psql stdout. `-X` does not replace
this ban.

### Pre-session mechanical validation

Before connecting, parse the constructed stdin bundle into its numbered
statements and require `actual_statement_sequence == frozen_statement_sequence`
exactly. Validation is sequence-based, not allowlist-membership-based. Reject a
missing, additional, duplicate, reordered, or unknown statement; any
line-leading backslash; any non-allowlisted function; and any
DDL/DML/LOCK/GRANT/REVOKE/COPY/DO/CALL/EXECUTE/PREPARE. If exact compliance is
unprovable, do not start production and authority remains unconsumed. The controller must fail fast after identity mismatch, Migration 0005 object
presence, Stage 0.32 drift, or a positive zero-row count. The controller may
stop after a failed gate, but the only valid transmitted
subsequences are prefixes of the frozen sequence; it may not generate a branch,
alternate order, runtime addition, or replacement query. If a repository
artifact is later created, record and verify its exact-byte SHA-256; until then
the numbered sequence below controls.

## Transaction and allowed operations

The single authorized PostgreSQL transaction must literally begin with P01
through P05 in the canonical executable bundle below. No substantive SELECT
may precede that prefix.

Only the exact frozen queries below are authorized. Non-SQL health evidence is
separately limited to non-mutating container inspection, service property reads,
and runtime.env metadata reads; it must not use arbitrary SQL or a shell launched
from psql. No synthetic business request or candidate traffic is allowed.

The following are prohibited: INSERT, UPDATE, DELETE, MERGE, TRUNCATE, ALTER,
CREATE, DROP, GRANT, REVOKE, COMMENT, VACUUM, ANALYZE, CLUSTER, REINDEX, unsafe
COPY TO/FROM external files, SET ROLE, `LOCK TABLE`, migration execution, and
stored-function invocation capable of mutation. Temporary mutation and “test
write then rollback” are prohibited. Migration 0004 must not be executed.

After all authorized reads, C01 in the canonical executable bundle harmlessly
closes the READ ONLY transaction. No alternate close example is executable or
authorized. The close cannot persist a change.

## Target identity must be first

The first substantive PostgreSQL evidence must prove, before any row count is
interpreted:

- `current_database() = 'aios'`;
- `current_user = 'aios'`;
- `current_schema() = 'public'` and the active
  schema context;
- `public.material_receipts` exists as the intended relation;
- the database, `public` schema, and target relation have the frozen expected
  owner `aios`;
- PostgreSQL is expected version `17.x`; and
- the session uses the frozen `aios-postgres` container/control plane.

A zero-row value from a wrong target is never evidence. Any identity mismatch
is **PREFLIGHT BLOCKED — STOP**.

## Separately frozen non-SQL health and runtime baseline

Before or alongside the database session, record non-secret, non-mutating proof:

- `aios-postgres` is running and healthy;
- container identity, start identity/time, and restart count;
- PostgreSQL responds normally and reports expected version 17.x;
- current `aios.service` state, PID, and start identity where available;
- `runtime.env` metadata/state only, without reading its contents;
- Telegram configuration/state and Universal Ingestion remain unchanged; and
- candidate production activation is absent.

Do not restart or mutate any container, PostgreSQL process, service, file,
integration, credential, production data, or traffic.

## Migration and Stage 0.32 pre-state

Catalog evidence must prove both
`public.material_receipts.created_by_actor_reference` and constraint
`material_receipts_created_by_actor_reference_valid` are absent. Either object
being present blocks eligibility: do not repair or continue toward execution.

Catalog evidence must also prove
`public.material_receipts_source_asset_active_uidx` is present, valid, ready,
and unique; has the sole logical key `source_asset_reference`; and has a
predicate semantically equivalent to excluding `REJECTED` and `CANCELLED`.
Any mismatch blocks. Migration 0004 must not be rerun.

## Zero-row hard gate and historical-row policy

Only after target identity, Migration 0005 absence, and Stage 0.32 index
verification pass, execute Z01 exactly as frozen in the canonical executable
bundle.

Only exact result `0` passes. Any positive result requires:

```text
PRODUCTION ACTOR-PROVENANCE PREFLIGHT BLOCKED
— EXISTING MATERIAL RECEIPTS REQUIRE HISTORICAL PROVENANCE GOVERNANCE
```

Then STOP with no Migration 0005 eligibility. It is prohibited to fabricate a
system, admin, migration, `aios`, unknown, zero-UUID, default-operator, or other
actor; introduce a temporary nullable migration; backfill; delete, rewrite, or
cancel rows. Historical rows require separate governance.

## Canonical four-table fingerprint

Capture only table name, row count, and deterministic digest for:

| Table | Stable primary-key order |
|---|---|
| `public.material_receipts` | `receipt_id` |
| `public.material_receipt_items` | `receipt_item_id` |
| `public.inventory_movements` | `movement_id` |
| `public.material_stock` | `material_id` |

Use exactly F01 through F04 in the canonical executable bundle, in that order;
runtime table/key substitution is forbidden.

Serialized rows must not leave PostgreSQL. For an empty table, require
`row_count = 0` and `row_digest = md5('')`; NULL or a missing digest is not
equivalent. An unavailable or incomparable fingerprint is INCONCLUSIVE.

## Schema, object, security, and role snapshots

Capture only the exact frozen, deterministically ordered catalog query set below for
the four governed tables: columns, types, nullability, defaults, constraints,
indexes, owners, ACLs, and non-internal triggers. Capture relevant `public`
functions and relations, the `public` schema, extensions, database/schema/table
ownership, roles and non-secret role attributes, memberships, ADMIN OPTION,
table privileges, and column privileges. Do not emit row contents.

The complete governed role set is exactly:

- `aios`;
- `aios_material_receipt_candidate_runtime`;
- `aios_material_receipt_candidate_writer`;
- `aios_material_inventory_posting_runtime`;
- `aios_material_inventory_posting_writer`; and
- `aios_material_stock_reader`.

Wildcard/open role discovery, including `rolname LIKE 'aios%'`, is prohibited.
Prove candidate runtime to candidate writer and posting runtime to posting writer,
the reader state, and ADMIN OPTION values. Unexpected expansion is BLOCKED.
Because the creator column must not yet exist, record its current privilege
pre-state without assuming it exists. The only permitted future Migration 0005
delta is candidate writer `INSERT(created_by_actor_reference)`; no role,
membership, ownership, ADMIN OPTION, unrelated ACL, creator UPDATE, posting
creator UPDATE, or reader-write change is expected.

## CANONICAL EXECUTABLE PREFLIGHT SQL BUNDLE

This is the one and only authoritative executable SQL sequence. The labels are
deterministic statement identifiers; every statement must remain at its frozen
position. All other SQL references in this package are NON-EXECUTABLE
EXPLANATION. No broad catalog dump is authorized.

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

-- I01 target identity and PostgreSQL version
SELECT current_database() AS database_name,
       current_user AS session_user,
       current_schema() AS schema_name,
       current_setting('server_version') AS server_version;

-- I02 database, schema, and relation identity and ownership
SELECT d.datname AS database_name, dr.rolname AS database_owner,
       n.nspname AS schema_name, nr.rolname AS schema_owner,
       c.relname AS relation_name, c.relkind AS relation_kind,
       cr.rolname AS relation_owner
FROM pg_catalog.pg_database AS d
JOIN pg_catalog.pg_roles AS dr ON dr.oid = d.datdba
JOIN pg_catalog.pg_namespace AS n ON n.nspname = 'public'
JOIN pg_catalog.pg_roles AS nr ON nr.oid = n.nspowner
JOIN pg_catalog.pg_class AS c
  ON c.relnamespace = n.oid AND c.relname = 'material_receipts'
JOIN pg_catalog.pg_roles AS cr ON cr.oid = c.relowner
WHERE d.datname = current_database()
ORDER BY d.datname, n.nspname, c.relname;

-- M01 Migration 0005 creator-column absence
SELECT a.attname AS column_name
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname = 'material_receipts'
  AND a.attname = 'created_by_actor_reference'
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY a.attname;

-- M02 Migration 0005 creator-constraint absence
SELECT con.conname AS constraint_name
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname = 'material_receipts'
  AND con.conname = 'material_receipts_created_by_actor_reference_valid'
ORDER BY con.conname;

-- S01 Stage 0.32 exact index
SELECT ci.relname AS index_name, i.indisvalid, i.indisready, i.indisunique,
       i.indnkeyatts,
       pg_catalog.pg_get_indexdef(i.indexrelid, 1, false) AS first_key_definition,
       pg_catalog.pg_get_expr(i.indpred, i.indrelid, false) AS predicate_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname = 'material_receipts'
  AND ci.relname = 'material_receipts_source_asset_active_uidx'
ORDER BY ci.relname;

-- Z01 zero-row hard gate
SELECT COUNT(*) AS material_receipts_count
FROM public.material_receipts;

-- F01 material_receipts fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY receipt_id), '')) AS row_digest
FROM public.material_receipts AS t;

-- F02 material_receipt_items fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY receipt_item_id), '')) AS row_digest
FROM public.material_receipt_items AS t;

-- F03 inventory_movements fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY movement_id), '')) AS row_digest
FROM public.inventory_movements AS t;

-- F04 material_stock fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY material_id), '')) AS row_digest
FROM public.material_stock AS t;

-- O01 four-table columns, types, nullability, and defaults
SELECT c.relname AS table_name, a.attnum AS ordinal_position,
       a.attname AS column_name,
       pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
       a.attnotnull AS not_null,
       pg_catalog.pg_get_expr(ad.adbin, ad.adrelid, false) AS default_definition
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_catalog.pg_attrdef AS ad
  ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY c.relname, a.attnum;

-- O02 four-table constraints
SELECT c.relname AS table_name, con.conname AS constraint_name,
       con.contype AS constraint_type,
       pg_catalog.pg_get_constraintdef(con.oid, false) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
ORDER BY c.relname, con.conname;

-- O03 four-table indexes
SELECT ct.relname AS table_name, ci.relname AS index_name,
       i.indisvalid, i.indisready, i.indisunique,
       pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition,
       pg_catalog.pg_get_expr(i.indpred, i.indrelid, false) AS predicate_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname IN ('material_receipts', 'material_receipt_items',
                     'inventory_movements', 'material_stock')
ORDER BY ct.relname, ci.relname;

-- O04 four-table owners and ACLs
SELECT c.relname AS table_name, r.rolname AS table_owner, c.relacl AS table_acl
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_roles AS r ON r.oid = c.relowner
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
ORDER BY c.relname;

-- O05 four-table non-internal triggers
SELECT c.relname AS table_name, t.tgname AS trigger_name,
       pg_catalog.pg_get_triggerdef(t.oid, false) AS trigger_definition
FROM pg_catalog.pg_trigger AS t
JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND NOT t.tgisinternal
ORDER BY c.relname, t.tgname;

-- O06 relevant trigger functions
SELECT c.relname AS table_name, t.tgname AS trigger_name,
       pn.nspname AS function_schema, p.proname AS function_name,
       pg_catalog.pg_get_functiondef(p.oid) AS function_definition
FROM pg_catalog.pg_trigger AS t
JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_proc AS p ON p.oid = t.tgfoid
JOIN pg_catalog.pg_namespace AS pn ON pn.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND NOT t.tgisinternal
ORDER BY c.relname, t.tgname, pn.nspname, p.proname;

-- O07 public schema owner and ACL
SELECT n.nspname AS schema_name, r.rolname AS schema_owner,
       n.nspacl AS schema_acl
FROM pg_catalog.pg_namespace AS n
JOIN pg_catalog.pg_roles AS r ON r.oid = n.nspowner
WHERE n.nspname = 'public'
ORDER BY n.nspname;

-- O08 extensions
SELECT e.extname AS extension_name, e.extversion AS extension_version,
       n.nspname AS extension_schema
FROM pg_catalog.pg_extension AS e
JOIN pg_catalog.pg_namespace AS n ON n.oid = e.extnamespace
ORDER BY e.extname;

-- R01 frozen role attributes
SELECT r.rolname, r.rolsuper, r.rolinherit, r.rolcreaterole,
       r.rolcreatedb, r.rolcanlogin, r.rolreplication, r.rolbypassrls
FROM pg_catalog.pg_roles AS r
WHERE r.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
ORDER BY r.rolname;

-- R02 frozen role memberships and ADMIN OPTION
SELECT mr.rolname AS member_name, gr.rolname AS granted_role_name, m.admin_option
FROM pg_catalog.pg_auth_members AS m
JOIN pg_catalog.pg_roles AS gr ON gr.oid = m.roleid
JOIN pg_catalog.pg_roles AS mr ON mr.oid = m.member
WHERE mr.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
   OR gr.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
ORDER BY mr.rolname, gr.rolname;

-- R03 frozen role table privileges
SELECT g.grantee, g.table_schema, g.table_name,
       g.privilege_type, g.is_grantable
FROM information_schema.role_table_grants AS g
WHERE g.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND g.table_schema = 'public'
  AND g.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY g.grantee, g.table_name, g.privilege_type;

-- R04 frozen role column privileges
SELECT p.grantee, p.table_schema, p.table_name, p.column_name,
       p.privilege_type, p.is_grantable
FROM information_schema.column_privileges AS p
WHERE p.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND p.table_schema = 'public'
  AND p.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY p.grantee, p.table_name, p.column_name, p.privilege_type;

-- C01 transaction close
COMMIT;
```

Only `current_setting('server_version')` is permitted. Required owners are
`aios`, relation kind is `r`, and version is 17.x. M01 and M02 must both return
zero rows. O06 only reads metadata for functions attached to non-internal
triggers on the exact tables; it never executes a function.

No password/verifier field is selected. No privilege function with arbitrary
role/table/column arguments is authorized.

## Evidence minimization and secret scan

Permitted evidence is limited to classifications, counts, hashes, digests, role
and object names, membership relationships, Boolean health states, PostgreSQL
version, container identity, and non-secret ownership/ACL summaries. Raw
business rows are prohibited.

Before classification, confirm the evidence contains no password, token, bot
token, API key, secret, credential-bearing DSN, `DATABASE_URL`, `runtime.env`
contents, private key, connection string, or password hash. If evidence cannot
be safely minimized, classify INCONCLUSIVE and STOP.
