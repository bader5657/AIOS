# Pre-Execution Gates and Locked One-Shot Transaction

## Stop-before-mutation gates

Immediately before execution, verify from clean synchronized main that this
authorization is merged and its exact reviewed commit is the approved source.
Recalculate both frozen migration hashes. Read-only target checks must prove the
same container identity, expected `postgres:17-alpine` image contract, healthy
state, governed production data mount, approved restart continuity, PostgreSQL
17.x, database/user `aios`, schema `public`, and required Migration 0002/0003
schema.

The new index must remain absent. The existing
`material_receipts_source_asset_idx` must remain present, non-unique, valid, and
keyed solely by `source_asset_reference`. An unexpected index, identity, schema,
source, hash, mount, health, or version state is **MIGRATION 0004 BLOCKED BEFORE
MUTATION**. Nothing may be repaired, dropped, or recreated under this authority.

Before entering the mutation transaction, repeat the canonical read-only counts
and digests for all four governed tables. They must exactly equal the frozen
preflight baseline: count zero and digest
`d41d8cd98f00b204e9800998ecf8427e` for every table. Any drift is **MIGRATION
0004 BLOCKED BEFORE MUTATION — AUTHORIZED PREFLIGHT BASELINE DRIFTED** and
requires a new read-only preflight and governance decision.

## One transaction and lock ordering

The one execution attempt uses exactly this transaction order:

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '5min';
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
LOCK TABLE public.material_receipts IN SHARE MODE;
```

Failure to acquire the lock within five seconds requires ROLLBACK and STOP. No
advisory lock, application SELECT lock, uncontrolled wait, or retry is allowed.
The final duplicate query runs only after successful SHARE-lock acquisition:

```sql
SELECT
    source_asset_reference,
    COUNT(*) AS active_count,
    ARRAY_AGG(receipt_id ORDER BY receipt_id) AS receipt_ids,
    ARRAY_AGG(status ORDER BY receipt_id) AS statuses
FROM public.material_receipts
WHERE status NOT IN ('REJECTED', 'CANCELLED')
GROUP BY source_asset_reference
HAVING COUNT(*) > 1;
```

Any row requires ROLLBACK and **MIGRATION 0004 BLOCKED BEFORE MUTATION — ACTIVE
DUPLICATE SOURCE DATA REQUIRES RECONCILIATION**. Winner selection, deletion,
rejection, cancellation, rewriting, or reconciliation is prohibited.

## Locked canonical baseline

After a zero-row final duplicate result, capture each governed table using the
already active canonical settings and exactly:

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

The exact stable orders are `material_receipts.receipt_id`,
`material_receipt_items.receipt_item_id`,
`inventory_movements.movement_id`, and `material_stock.material_id`. Only table
name, count, and digest may leave PostgreSQL. The locked values must still be
zero / `d41d8cd98f00b204e9800998ecf8427e`; otherwise ROLLBACK and the baseline-
drift classification apply.

Before DDL, also capture bounded structured catalogs for relevant indexes,
database/schema/table owners, candidate/posting/reader/admin role existence,
memberships, ACLs, non-internal triggers, associated user functions, schemas,
extensions, and governed relations. Passwords and authentication secrets must
not be queried or emitted.

## Exact artifact execution

Only after every prior gate passes may the fixed control plane execute the exact
hash-verified UP artifact through approved stdin/file input. It must not be
reconstructed from this document. The execution session may perform no other
mutation.
