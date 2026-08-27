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

Every preservation capture uses its own explicit transaction and establishes
the following canonical representation settings transaction-locally:

```sql
BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
```

Persistent `ALTER DATABASE`, `ALTER ROLE`, and `postgresql.conf` changes are
prohibited. A digest produced without all four settings is not comparable and
must be classified inconclusive.

After setting them, capture each table with this one canonical procedure,
substituting only the frozen table and primary-key names below:

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

The transaction then runs the active-duplicate query and commits without
mutation. The same exact settings and query shape are mandatory for the
read-only preflight, the locked transaction's before- and after-DDL captures,
and separate post-deployment verification.

The frozen table and stable primary-key order substitutions are:

| Table | Deterministic order |
|---|---|
| `public.material_receipts` | `receipt_id` |
| `public.material_receipt_items` | `receipt_item_id` |
| `public.inventory_movements` | `movement_id` |
| `public.material_stock` | `material_id` |

No unordered aggregate, `ctid`, insertion order, timestamp order, or
planner-dependent order is permitted. `row_to_json` encodes each complete row;
SQL NULL becomes JSON `null` and remains distinct from an empty string, the
string `"null"`, zero, and false. Business columns must not be individually
coalesced. Only the aggregate NULL for an empty table is converted to `''`, so
the frozen empty-table result is `row_count = 0` and `row_digest = md5('')`.

The row JSON also escapes control characters and newlines within business
values, while the separator between complete JSON rows is exactly `E'\n'`.
Raw column concatenation such as `col1 || '|' || col2` is prohibited. Current
governed tables contain `TIMESTAMPTZ` values, which are serialized only after
`TimeZone = UTC`, and `material_receipts` contains `DATE` values, serialized
only with `DateStyle = 'ISO, YMD'`. Thus the procedure does not depend on host,
operator, role, database, or session defaults.

Only table name, count, and digest leave PostgreSQL; serialized rows and
business values never do. If the settings cannot be established, the query
differs, stable primary-key ordering is unavailable, calculation fails, or the
before/after algorithms differ, classify **PRESERVATION VERIFICATION
INCONCLUSIVE — STOP**. Fingerprint verification cannot be waived or replaced by
row counts automatically, and no extension may be installed to obtain it.

Before production authority, verifier readiness must be demonstrated against
disposable PostgreSQL: sessions initially using `Asia/Jakarta`, `UTC`, and
`America/New_York` must produce identical digests after applying the canonical
transaction-local settings. Differing initial `DateStyle` values must likewise
be tested where practical. This adversarial readiness proof is not a production
query and is not executed by this governance package.

## Preflight classifications

- **A — PRODUCTION DUPLICATE PREFLIGHT PASS — ZERO ACTIVE DUPLICATE SOURCES —
  ELIGIBLE FOR MIGRATION 0004 EXECUTION AUTHORIZATION**
- **B — PRODUCTION DUPLICATE PREFLIGHT BLOCKED — ACTIVE DUPLICATE SOURCE DATA
  REQUIRES RECONCILIATION**
- **C — PRODUCTION PREFLIGHT INCONCLUSIVE — ENVIRONMENT / SCHEMA / IDENTITY
  MISMATCH**

Only A permits a separate migration-execution authority request.
