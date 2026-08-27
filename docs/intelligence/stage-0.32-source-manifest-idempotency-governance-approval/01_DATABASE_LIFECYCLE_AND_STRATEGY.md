# Stage 0.32 Database, Lifecycle, and Idempotency Contract

## Frozen database enforcement

The future schema change is exactly:

```sql
CREATE UNIQUE INDEX material_receipts_source_asset_active_uidx
ON material_receipts (source_asset_reference)
WHERE status NOT IN ('REJECTED', 'CANCELLED');
```

It is the authoritative concurrency mechanism. `SELECT` followed by `INSERT`
without database enforcement is not sufficient.

The existing `material_receipts_source_asset_idx` is retained unchanged in this
stage unless later governance explicitly approves its removal.

## Lifecycle semantics

| Transition/state | Source key behavior |
|---|---|
| ACTIVE → ACTIVE | Key remains occupied |
| ACTIVE → REJECTED | Key is released; row remains history |
| ACTIVE → CANCELLED | Key is released; row remains history |
| REJECTED/CANCELLED | Historical row remains stored |
| After all prior rows terminal | New receipt may use the source key |

There is no automatic deletion, row reuse, or receipt-ID reuse. Governed
candidate lifecycle continues to prohibit terminal-to-active reactivation. Any
future reactivation proposal requires separate governance and remains subject to
the same unique index.

## Strategy comparison

### Partial unique index — APPROVED

This is the simplest PostgreSQL-native solution. It atomically serializes
identical active inserts, supports terminal replacement, preserves history,
requires no new runtime privilege, and has minimal migration surface.

### Dedicated idempotency table

It could work, but would introduce a second source of truth, lifecycle-release
logic, additional transaction coupling, and more privilege/maintenance burden.
It is not selected for v1.

### Advisory locking

Advisory locks alone are not durable enforcement: every writer must cooperate and
the invariant is not represented in the data model. Advisory locking combined
with the unique index adds complexity without improving correctness for v1.

## Duplicate create contract

The public bounded outcome is `SOURCE_ACTIVE_RECEIPT_EXISTS`. It is returned for
an existing active receipt in `EXTRACTED`, `NEEDS_REVIEW`, `CONFIRMED`, or
`POSTED` state. Create never returns the existing row, compares business facts,
or mutates it. Corrections use governed revision/review operations.

The repository must identify only the approved source-active unique violation.
Unrelated unique or integrity failures remain their existing bounded integrity
outcome. SQLSTATE, SQL, index/constraint names, DSNs, credentials, and Psycopg
objects are never public.

## Source and registry authority

The deduplication key is exclusively the canonical retained
`source_asset_reference` produced by Stage 0.31A. `registry_record_id` remains
optional corroborating identity and never becomes the deduplication authority.

