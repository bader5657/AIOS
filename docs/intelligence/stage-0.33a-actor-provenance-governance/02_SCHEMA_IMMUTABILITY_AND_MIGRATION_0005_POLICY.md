# Schema Immutability and Migration 0005 Policy

## Frozen schema contract

The expected future schema addition is:

```sql
created_by_actor_reference TEXT NOT NULL
```

on `public.material_receipts`, with a database `CHECK` correctly enforcing the exact `operator:<lowercase-uuidv4>` contract. This database requirement is mandatory unless a separate governance decision explicitly approves a weaker database contract. The field uses the receipt's existing `created_at` as its authoritative timestamp; no provenance timestamp or separate provenance record is introduced.

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

## Non-weakenable database enforcement

Migration 0005 must enforce at the PostgreSQL layer the exact ASCII `operator:` prefix, canonical lowercase hyphenated UUID text, and UUID version 4. A superficial regular expression that also accepts UUIDv1, UUIDv3, UUIDv5, uppercase UUIDs, malformed UUIDs, noncanonical forms, or arbitrary operator identifiers is not compliant. Application validation alone may not silently substitute for this frozen database requirement.

If implementation cannot correctly enforce every frozen property, implementation of the weakened `CHECK` must stop. The exact limitation must be documented and explicit Project Owner/governance approval obtained before any weaker database enforcement may merge.

Disposable PostgreSQL tests must exercise the actual constraint. They must accept `operator:<valid-lowercase-canonical-uuidv4>` and reject uppercase UUIDv4, UUIDv1, UUIDv3 where constructible, UUIDv5, the zero UUID, malformed UUIDs, missing-hyphen and braced forms, leading/trailing whitespace, `reviewer:<valid-uuidv4>`, `system:<valid-uuidv4>`, blank text, and `NULL` under the `NOT NULL` constraint.

## Production DOWN policy

A future Migration 0005 `DOWN` may exist only for disposable PostgreSQL lifecycle tests and development/test rollback verification. Stage 0.33A does not authorize production `DOWN`.

After provenance-bearing production receipts exist, removing `created_by_actor_reference` would destroy durable audit provenance. Any production removal therefore requires separate destructive rollback governance covering:

- the explicit reason;
- production row and data assessment;
- provenance-loss impact;
- rollback authorization;
- preservation/export policy where applicable; and
- explicit Project Owner approval.

There is no automatic production `DOWN`, no deploy-failure fallback that drops provenance after a committed migration, and no generic rollback authority.

## Exact runtime privilege matrix

The future candidate writer/runtime is authorized only for the narrow insert columns required for candidate creation, including `created_by_actor_reference`. It is not authorized to update, erase, or rewrite creator provenance; perform generic or unrelated provenance writes; post; mutate movements or stock; administer the database; own database objects; execute DDL; or exercise grant option.

The posting writer/runtime is not authorized to update `created_by_actor_reference`. No runtime identity may mutate original creator provenance after insertion.

## Zero-row and historical-data stop clarification

The simple `NOT NULL`, no-backfill production path is available only when the separately authorized, immediate read-only count returns the scalar value `0`. A positive count is a hard stop: there is no implementation-time workaround, automatic alternate strategy, temporary nullable-column path, or fabricated backfill under this authority. Historical rows require separate historical-data governance.

## Stage 0.32 preservation

Migration 0005 must leave `material_receipts_source_asset_active_uidx`, its uniqueness, its predicate, and `SOURCE_ACTIVE_RECEIPT_EXISTS` behavior unchanged. Disposable tests and the separately governed future production verifier must prove this preservation. Migration 0005 must also preserve existing indexes, unrelated columns, triggers, functions, roles, ownership, unrelated ACLs, and business data.

Stage 0.32 remains closed. Migration 0004 must not be changed or rerun.
