# Schema Immutability and Migration 0005 Policy

## Frozen schema contract

The expected future schema addition is:

```sql
created_by_actor_reference TEXT NOT NULL
```

on `public.material_receipts`, with a database `CHECK` enforcing the exact `operator:<lowercase-uuidv4>` contract where that constraint is practical and correctly expressible. The field uses the receipt's existing `created_at` as its authoritative timestamp; no provenance timestamp or separate provenance record is introduced.

The expected next migration number is Migration 0005, **subject to implementation-time migration inventory confirmation**. No Migration 0005 file is created or authorized by this governance package. Migration 0004 has already been deployed once and must not be executed again.

No index is authorized unless an actual, separately approved query requirement demonstrates a need. No provenance read API is authorized in v1.

## Immutability

`created_by_actor_reference` is immutable after receipt creation. Revision, review, confirmation, rejection, cancellation, and posting must not modify it. No generic `UPDATE` surface may expose the field.

Candidate and posting runtime roles receive no `UPDATE` authority over creator provenance. Database-owner intervention remains exceptional, governance-only authority; it is not a runtime path or ordinary repair mechanism.

## Transaction atomicity

The future implementation must insert the creator reference inside the existing candidate receipt-creation transaction:

```text
receipt + items + creator provenance
→ COMMIT together
or
→ ROLLBACK together
```

No production-created candidate receipt may exist without provenance. Because provenance is a receipt column, there is no orphan-provenance concept.

## Stage 0.32 idempotency interaction

Stage 0.32 remains unchanged and authoritative. `created_by_actor_reference` is not part of source deduplication.

If operator B attempts the same source while operator A owns the active receipt, the result remains `SOURCE_ACTIVE_RECEIPT_EXISTS`:

- no second receipt is created;
- no provenance is overwritten; and
- the response does not disclose operator A's identity.

## Terminal replacement

A rejected or cancelled historical receipt retains its original creator. A legitimate replacement receipt receives its own newly authenticated creator reference. Provenance is never inherited or copied from the terminal receipt.

## Production zero-row preflight

Production deployment of Migration 0005 requires a separately authorized, read-only preflight immediately before deployment. The simple `NOT NULL`, no-backfill deployment path requires this production query to establish zero rows:

```sql
SELECT COUNT(*) FROM public.material_receipts;
```

Required result:

```text
0 rows
```

If `row_count > 0`, deployment must stop. Migration 0005 must not be deployed, no provenance may be invented, and separate historical-data governance is required.

## Prohibited backfill

No backfill is authorized. Synthetic historical creator attribution is prohibited, including `system`, `admin`, `aios`, `migration`, `unknown operator`, `default operator`, or any equivalent fabricated identity.

## Privilege contract

A future candidate writer may receive only the narrowly required `INSERT` authority needed to populate `created_by_actor_reference`. This decision grants:

- no provenance `UPDATE`;
- no generic audit write;
- no posting, movement, stock, or admin privilege expansion; and
- no database-owner change from any runtime path.

This package itself authorizes no role, grant, ownership, or PostgreSQL change.
