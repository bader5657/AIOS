# Read-Only Database Verification Contract

## Fixed control plane and transaction

The one future session must use only:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

SQL is supplied by approved stdin/file input without credentials. Host `psql`,
host sockets, `sudo -u postgres`, external endpoints, password-bearing URIs, and
caller-selected container/database/role fallbacks are prohibited.

All production SQL runs within exactly:

```sql
BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
-- bounded SELECT verification only
COMMIT;
```

No explicit table lock or write-blocking migration lock is authorized. Any SQL
error, identity mismatch, or inability to establish read-only/canonical settings
requires rollback if active, STOP, and an inconclusive/blocked classification.

## Identity, health, and index structure

The session must prove PostgreSQL 17.x, database/user `aios`, schema `public`,
and all four governed tables. Structured `pg_catalog` evidence must prove:

- `public.material_receipts_source_asset_active_uidx` exists, is valid, ready,
  unique, belongs exactly to `public.material_receipts`, has one key column
  exactly `source_asset_reference`, and has a predicate semantically equivalent
  to `status NOT IN ('REJECTED', 'CANCELLED')`; and
- `public.material_receipts_source_asset_idx` remains present, valid, ready,
  non-unique, and keyed solely by `source_asset_reference`.

No repair or modification is permitted. A new-index mismatch is
**POST-DEPLOYMENT VERIFICATION BLOCKED — PRODUCTION INDEX STATE MISMATCH**.

## Canonical business preservation

The authoritative locked pre-DDL and transaction after-DDL values were:

| Table | Row count | Row digest |
|---|---:|---|
| `public.material_receipts` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.material_receipt_items` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.inventory_movements` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.material_stock` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |

With the canonical settings active, recapture each table exactly as:

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

The exact orders are `material_receipts.receipt_id`,
`material_receipt_items.receipt_item_id`,
`inventory_movements.movement_id`, and `material_stock.material_id`. Counts and
digests must exactly equal the locked baseline. No row-count-only fallback is
allowed. Any mismatch or incomparable calculation is **PRESERVATION
VERIFICATION FAILED / INCONCLUSIVE — STOP**. Only table name, count, and digest
may leave PostgreSQL; serialized business rows must not.

## Active-duplicate postcheck

Run exactly:

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

Zero rows are required. Any result is **POST-DEPLOYMENT VERIFICATION BLOCKED —
ACTIVE DUPLICATE PRODUCTION DATA DETECTED**. Reconciliation, winner selection,
deletion, cancellation, rejection, rewriting, or migration rerun is prohibited.

## Security and object preservation

Bounded structured evidence must confirm the database/schema/table owners,
candidate/posting/reader/admin roles and non-secret attributes, memberships,
ACLs, non-internal triggers, relevant user-defined functions, schemas,
extensions, governed relations, and unrelated indexes remain at the execution
baseline. Candidate runtime `aios_material_receipt_candidate_runtime` must have
no posting/admin membership; posting roles remain separate. The approved new
index is the only intended pre-migration schema difference.

The execution transaction produced identical before/after bounded snapshot
digests. The post-deployment verifier must reproduce the same projections,
ordering, canonical settings, and exclusions and require these frozen values:

| Snapshot | Execution digest |
|---|---|
| Governed indexes, excluding the separately verified new index | `7df74340faad2243bc1d882b01041e75` |
| Database/schema/table ownership and ACLs | `3477e5fbfeca35e7aed45bae17990467` |
| Relevant role attributes | `65cbf0f753fc942d636edba8bf443f75` |
| Relevant memberships | `8882f55ea69746e789f960881f301818` |
| Non-internal governed-table triggers | `d41d8cd98f00b204e9800998ecf8427e` |
| Relevant public user-defined functions | `d41d8cd98f00b204e9800998ecf8427e` |
| Public schema and extensions | `093bc6d4016f7335c21b23f8789f9eff` |
| Public non-index relations | `a51c24af830e4f3ad62ec26172ed1dc3` |

The new active-source index is verified structurally on its own and excluded
from the governed/unrelated-index digest exactly as it was after DDL. No other
snapshot exclusion or algorithm change is allowed; an incomparable snapshot is
inconclusive and blocks closure.

Passwords, password hashes, authentication secrets, DSNs, credentials, and
business-row contents must not be queried or emitted. A preservation mismatch
blocks closure and grants no corrective authority.
