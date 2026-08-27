# Verification, Commit, Consumption, and Remaining Gates

## Structural verification before commit

After the exact UP DDL, structured `pg_catalog` evidence inside the same
transaction must prove:

- `public.material_receipts_source_asset_active_uidx` exists, is valid/ready and
  unique, belongs exactly to `public.material_receipts`, has one key column
  exactly `source_asset_reference`, and has the approved active-status predicate;
- `public.material_receipts_source_asset_idx` remains valid/ready, non-unique,
  and keyed solely by `source_asset_reference`; and
- no unrelated index, relation, schema, trigger, function, extension, role,
  membership, owner, or ACL changed.

SQL-text grep is not structural proof. Any mismatch requires ROLLBACK.

## Business and security preservation

Using the unchanged canonical settings and exact fingerprint procedure, capture
all four after-DDL counts/digests. For every table require both:

```text
after_count  == locked_before_count
after_digest == locked_before_digest
```

Under this authority each expected count remains zero and each digest remains
`d41d8cd98f00b204e9800998ecf8427e`. A mismatch or incomparable fingerprint is
**PRESERVATION VERIFICATION INCONCLUSIVE / FAILED — STOP** and requires
ROLLBACK.

Compare the bounded before/after security/object catalogs. Candidate, posting,
reader and administrative roles; memberships; owners; ACLs; triggers;
functions; schemas; extensions; and unrelated relations/indexes must be
unchanged. Password/authentication state is neither queried nor modified. Only
the approved new index may differ.

## Commit condition

COMMIT is permitted only when all of the following pass in the one governed
attempt:

1. source, authorization merge, hashes, target, health, identity and schema;
2. external-preflight continuity before transaction entry;
3. bounded SHARE-lock acquisition;
4. zero locked active-duplicate groups;
5. accepted locked before-DDL baseline;
6. exact frozen UP artifact execution;
7. new-index structural verification;
8. existing-index preservation;
9. four-table count/digest preservation; and
10. role/ACL/ownership/object preservation.

Any pre-COMMIT failure requires ROLLBACK if active, STOP, bounded classification,
and return to governance. There is no automatic retry and DOWN is not
authorized. A committed index may be removed only under separate rollback
governance.

## One-shot consumption and classifications

Exactly one production execution attempt is authorized after activation. Once
the governed mutation session enters sensitive execution/DDL attempt, the
authority is consumed whether the result commits, rolls back, or blocks after
session entry. A second attempt requires new governance.

The only result classifications are:

- **MIGRATION 0004 DEPLOYED AND VERIFIED — POST-DEPLOYMENT VERIFICATION STILL
  REQUIRED**;
- **MIGRATION 0004 FAILED — TRANSACTION ROLLED BACK**; or
- **MIGRATION 0004 BLOCKED BEFORE MUTATION**.

No ambiguous or partial-success classification is allowed.

## Separate post-deployment authority

Successful COMMIT does not close the operational gate. A separate read-only
post-deployment authority must verify production health, exact new-index
structure, zero active duplicates, equality with the locked before-DDL business
baseline, preservation of the existing index and roles/grants/owners, unchanged
service/runtime/Telegram/Universal Ingestion state, and no candidate activation.

The source-manifest idempotency operational gate remains OPEN until governance,
preflight, one-shot migration, and separate post-deployment verification all
pass. The following also remain independently OPEN:

- durable candidate-creation actor provenance;
- runtime-secret rotation / activation safety; and
- explicit production safety review.

Production candidate activation remains **NOT AUTHORIZED**.

Publication status: **STAGE 0.32 MIGRATION 0004 ONE-SHOT EXECUTION AUTHORIZATION
PROPOSED — READY FOR INDEPENDENT AUTHORIZATION REVIEW / MERGE — MIGRATION 0004
NOT YET EXECUTED**.
