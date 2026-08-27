# Locked One-Shot Transaction and Verification Contract

## TOCTOU control and lock decision

The external read-only preflight is not the final correctness guard. A future
authorized executor must acquire:

```sql
LOCK TABLE public.material_receipts IN SHARE MODE;
```

`SHARE` is the narrowest sufficient table lock for this migration. It conflicts
with the `ROW EXCLUSIVE` lock acquired by INSERT, UPDATE, and DELETE, including
mutations of `source_asset_reference` or `status`, while continuing to permit
ordinary reads. It is also the lock mode required by non-concurrent
`CREATE INDEX`; no advisory lock, application SELECT lock, or stronger
`ACCESS EXCLUSIVE` lock is approved.

Set transaction-local bounds before lock acquisition:

```sql
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '5min';
```

Failure to acquire the lock within five seconds, or any statement timeout,
requires ROLLBACK and STOP. The values are frozen for governance review; changing
them requires new authority. There is no uncontrolled wait or automatic retry.

## One explicit transaction

A later one-shot execution authority must preserve this order:

1. verify the frozen source commit, migration hashes, container health/identity,
   fixed transport, PostgreSQL/database/user/schema, prerequisites, target-table
   identity, and pre-DDL index state;
2. `BEGIN` and set the transaction-local timeouts;
3. acquire `SHARE` on `public.material_receipts`;
4. re-run the exact active-duplicate query under the lock;
5. if any duplicate exists, `ROLLBACK` and STOP before mutation;
6. capture inside-transaction before-state counts, deterministic fingerprints,
   and bounded catalogs for indexes, roles, memberships, ownership, ACLs,
   triggers, functions, and schemas;
7. supply and execute the exact frozen 0004 UP SQL;
8. run structural and preservation verification inside the same transaction;
9. `COMMIT` only if every assertion passes.

Use normal `READ COMMITTED`: acquire the table lock before the final duplicate
query and preservation snapshot so transactions that committed before lock
acquisition are visible and no subsequent receipt writer can pass the lock.

## Structural verification before commit

Structured `pg_catalog` evidence must prove:

- `public.material_receipts_source_asset_active_uidx` exists;
- its relation is exactly `public.material_receipts`;
- `indisunique` is true;
- its sole key column is exactly `source_asset_reference`;
- `pg_get_expr(indpred, indrelid)` is semantically the approved active predicate;
- `public.material_receipts_source_asset_idx` still exists, has the same sole
  key column, and remains non-unique; and
- before/after bounded catalogs show no unexpected trigger, function, role,
  membership, grant, ownership, schema, extension, or secondary relation change.

Verification must use structured catalog fields, not human-readable error or
DDL-message parsing. Any mismatch rolls back the transaction.

## Business-data preservation

Immediately before and after index creation, compare the four row counts and
the approved deterministic fingerprints for `material_receipts`,
`material_receipt_items`, `inventory_movements`, and `material_stock`. All must
be identical. The transaction is not authorized to issue a business-data
INSERT, UPDATE, DELETE, cancellation, rejection, reconciliation, or winner
selection.

## Attempt, rollback, and DOWN policy

Future execution authority permits exactly one controlled attempt. Any failure
before commit requires transaction ROLLBACK, classified evidence, STOP, and
return to governance. The authority is consumed; there is no automatic retry.

The DOWN migration is not part of normal deployment and is not an automatic
compensation after a committed UP. A later removal of the index requires
separate rollback authority. A successfully committed authority is consumed.

## Execution classifications

- **A — MIGRATION 0004 DEPLOYED AND VERIFIED**
- **B — MIGRATION 0004 FAILED — TRANSACTION ROLLED BACK**
- **C — MIGRATION 0004 BLOCKED BEFORE MUTATION**

No ambiguous success classification is allowed.
