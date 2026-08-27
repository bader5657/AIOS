# Read-Only Production Preflight and Active-Duplicate Stop Gate

## Separate authority

This package does not execute or authorize production queries. After this
governance package is independently reviewed and merged, a separate narrow
READ-ONLY authority may permit one preflight session. A passing preflight is
evidence for considering a later one-shot migration authority; it is not DDL
authority.

## Identity, health, and schema gates

Before any later DDL authority, the read-only preflight must prove:

1. source is clean and synchronized to the governance-approved main commit;
2. both migration hashes equal the package-control values;
3. container `aios-postgres` is running and healthy, with identity, image,
   restart count, and expected production storage identity recorded;
4. the fixed container-local control plane reaches PostgreSQL 17.x, database
   `aios`, administrative identity `aios`, and schema `public`;
5. `public.material_receipts`, `public.material_receipt_items`,
   `public.inventory_movements`, and `public.material_stock` exist with the
   approved Migration 0002/0003 schema baseline;
6. `public.material_receipts_source_asset_active_uidx` is absent;
7. `public.material_receipts_source_asset_idx` exists on exactly
   `source_asset_reference` and is non-unique; and
8. no schema, identity, ownership, ACL, trigger, function, or migration-number
   ambiguity exists.

An unhealthy container, wrong database/user/schema/version/storage target,
missing prerequisite, unexpected existing 0004 index, schema drift, dirty
source, or hash mismatch is outcome C and requires STOP without mutation.

## Authoritative active-duplicate query

The frozen query is:

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

Zero rows means the preflight may be classified A. Any row is a HARD STOP and
classification B. No winner selection, deletion, cancellation, rejection,
merge, source-reference rewrite, or automatic reconciliation is authorized.
Existing conflicts require a separate data-reconciliation governance package.

## Evidence minimization

Normal evidence contains only target/identity results, schema/index state,
aggregate table row counts, duplicate group count, and bounded fingerprints.
Source references, receipt IDs, and statuses are included only when conflicts
exist and are required for separately governed reconciliation. Evidence never
contains credentials, runtime configuration values, DSNs, supplier/document
details, receipt-item contents, source-document contents, or unrelated rows.

## Read-only preservation baseline

Capture row counts for all four business tables. Where the baseline schema and
size permit, compute a deterministic server-side fingerprint for each table as
`md5(string_agg(row_to_json(t)::text, E'\n' ORDER BY <primary_key>))`, using:

| Table | Deterministic order |
|---|---|
| `public.material_receipts` | `receipt_id` |
| `public.material_receipt_items` | `receipt_item_id` |
| `public.inventory_movements` | `movement_id` |
| `public.material_stock` | `material_id` |

Only count and digest leave PostgreSQL. If a bounded fingerprint cannot be
computed safely, record that fact and require exact row-count preservation plus
an approved alternative before migration authority. Do not install an extension
or expose business rows to obtain a fingerprint.

## Preflight classifications

- **A — PRODUCTION DUPLICATE PREFLIGHT PASS — ZERO ACTIVE DUPLICATE SOURCES —
  ELIGIBLE FOR MIGRATION 0004 EXECUTION AUTHORIZATION**
- **B — PRODUCTION DUPLICATE PREFLIGHT BLOCKED — ACTIVE DUPLICATE SOURCE DATA
  REQUIRES RECONCILIATION**
- **C — PRODUCTION PREFLIGHT INCONCLUSIVE — ENVIRONMENT / SCHEMA / IDENTITY
  MISMATCH**

Only A permits a separate migration-execution authority request.
