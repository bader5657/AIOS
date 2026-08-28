# Stage 0.33B-P Read-Only Query and Evidence Contract

## Transaction and allowed operations

The single authorized PostgreSQL transaction must literally begin:

```sql
BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
```

Only bounded `SELECT`, PostgreSQL catalog inspection, and non-mutating
health/status reads are authorized. Health may be established only through
bounded SELECT, container/status inspection, and process/service metadata; no
synthetic business request or candidate traffic is permitted.

The following are prohibited: INSERT, UPDATE, DELETE, MERGE, TRUNCATE, ALTER,
CREATE, DROP, GRANT, REVOKE, COMMENT, VACUUM, ANALYZE, CLUSTER, REINDEX, unsafe
COPY TO/FROM external files, SET ROLE, `LOCK TABLE`, migration execution, and
stored-function invocation capable of mutation. Temporary mutation and “test
write then rollback” are prohibited. Migration 0004 must not be executed.

After all authorized reads, `COMMIT;` or `ROLLBACK;` may harmlessly close the
READ ONLY transaction. Neither path may persist a change.

## Target identity must be first

The first substantive PostgreSQL evidence must prove, before any row count is
interpreted:

- `current_database() = 'aios'`;
- `current_user = 'aios'`;
- `current_schema() = 'public'`, or structured equivalent proof of the active
  schema context;
- `public.material_receipts` exists as the intended relation;
- the database, `public` schema, and target relation have the frozen expected
  owner `aios`;
- PostgreSQL is expected version `17.x`; and
- the session uses the frozen `aios-postgres` container/control plane.

A zero-row value from a wrong target is never evidence. Any identity mismatch
is **PREFLIGHT BLOCKED — STOP**.

## Bounded health and runtime baseline

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

Only after target identity passes, execute exactly:

```sql
SELECT COUNT(*)
FROM public.material_receipts;
```

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

Use the transaction settings above and exactly this procedure for each table:

```sql
SELECT
    COUNT(*) AS row_count,
    md5(
        COALESCE(
            string_agg(
                row_to_json(t)::text,
                E'\n'
                ORDER BY <PRIMARY_KEY>
            ),
            ''
        )
    ) AS row_digest
FROM <TABLE> AS t;
```

Serialized rows must not leave PostgreSQL. For an empty table, require
`row_count = 0` and `row_digest = md5('')`; NULL or a missing digest is not
equivalent. An unavailable or incomparable fingerprint is INCONCLUSIVE.

## Schema, object, security, and role snapshots

Capture structured, deterministically ordered, non-secret catalog evidence for
the four governed tables: columns, types, nullability, defaults, constraints,
indexes, owners, ACLs, and non-internal triggers. Capture relevant `public`
functions and relations, the `public` schema, extensions, database/schema/table
ownership, roles and non-secret role attributes, memberships, ADMIN OPTION,
table privileges, and column privileges. Do not emit row contents.

The minimum governed role set is:

- `aios_material_receipt_candidate_runtime` and
  `aios_material_receipt_candidate_writer`;
- `aios_material_inventory_posting_runtime` and
  `aios_material_inventory_posting_writer`;
- `aios_material_stock_reader`; and
- other directly relevant `aios` roles needed to prove the privilege baseline.

Prove candidate runtime → candidate writer and posting runtime → posting
writer relationships, the reader relationship/state, and all relevant ADMIN
OPTION values. Unexpected membership or privilege expansion blocks.

Because the creator column must not yet exist, record its current privilege
pre-state without assuming it exists. The only permitted future Migration 0005
delta is candidate writer `INSERT(created_by_actor_reference)`; no role,
membership, ownership, ADMIN OPTION, unrelated ACL, creator UPDATE, posting
creator UPDATE, or reader-write change is expected.

## Evidence minimization and secret scan

Permitted evidence is limited to classifications, counts, hashes, digests, role
and object names, membership relationships, Boolean health states, PostgreSQL
version, container identity, and non-secret ownership/ACL summaries. Raw
business rows are prohibited.

Before classification, confirm the evidence contains no password, token, bot
token, API key, secret, credential-bearing DSN, `DATABASE_URL`, `runtime.env`
contents, private key, connection string, or password hash. If evidence cannot
be safely minimized, classify INCONCLUSIVE and STOP.
