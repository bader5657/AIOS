# One-Shot Migration 0005 Transaction and Verification

## Activation and consumption

0.33B-A requires merged 0.33B-G governance, a fresh 0.33B-P PASS, zero receipt
rows, absent creator column/CHECK, healthy Stage 0.32 index, synchronized clean
main, exact UP hash, production health, captured preservation and role/ACL
baselines, explicit Project Owner approval, and zero unresolved blockers.

It permits exactly one Migration 0005 UP attempt. Authority is consumed when
the first sensitive DDL execution begins, regardless of outcome. Failure means
ROLLBACK/STOP and return to governance: no automatic retry and no automatic or
production DOWN.

## Transaction and lock strategy

Migration 0005 contains ordinary `ALTER TABLE` and `GRANT`; PostgreSQL supports
both transactionally. It contains no `CREATE INDEX CONCURRENTLY` or other
non-transactional command. The future executor must use one explicit
`READ COMMITTED` transaction:

```sql
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
LOCK TABLE public.material_receipts IN ACCESS EXCLUSIVE MODE;
```

`ALTER TABLE ... ADD COLUMN ... NOT NULL` requires ACCESS EXCLUSIVE, so taking
that exact lock explicitly before the final checks closes the preflight/DDL
race. The five-second lock timeout avoids an uncontrolled wait. Thirty seconds
is a conservative statement bound for the mandatory empty table. Either
timeout causes ROLLBACK/STOP with no retry under the consumed authority.

## Locked immediate recheck

After the lock and before DDL, recheck in structured form:

1. receipt row count is exactly zero;
2. creator column and named constraint remain absent;
3. Stage 0.32 index remains present, valid, ready, unique, sole-keyed on
   `source_asset_reference`, with unchanged predicate;
4. target/database/schema/owner identity remains exact; and
5. critical data and security/object baselines remain consistent with the
   preflight.

Any drift stops before DDL. Ordinary reads may be blocked briefly by ACCESS
EXCLUSIVE; production candidate traffic must remain unauthorized and absent.

## Exact artifact and pre-COMMIT verifier

Immediately before execution, verify the committed UP artifact SHA-256 equals
`7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`.
Execute that file directly through the fixed control plane. Reconstructed,
copied, edited, or temporary SQL is prohibited.

Before COMMIT, structured PostgreSQL catalogs—not source parsing alone—must
prove:

- creator column exists on `public.material_receipts`, type is `text`, NOT NULL
  is true, and no default exists;
- exact constraint `material_receipts_created_by_actor_reference_valid` exists
  and its catalog definition matches the reviewed lowercase canonical RFC4122
  UUIDv4 grammar;
- no provenance index, trigger, function, table, or other object was added;
- Stage 0.32 index is unchanged;
- candidate writer has INSERT, but not UPDATE, on the creator column;
- candidate runtime inherits that INSERT only through the expected writer
  membership; posting runtime has no creator UPDATE; reader remains read-only;
- roles, memberships, ADMIN OPTION, owners, unrelated ACLs, triggers,
  functions, schemas/extensions, relations, and unrelated indexes/constraints
  match the locked before-state except the exact approved column/CHECK/grant;
- all four business-table counts and canonical digests equal their locked
  before-state values; and
- no business row was created.

Production verification must not INSERT synthetic rows to exercise the CHECK.
Its behavior is already proven on disposable PostgreSQL; production verification
is structural and catalog-based.

## Commit and rollback policy

COMMIT is permitted only when source/main/hash, target identity, locked zero-row
recheck, exact artifact execution, column/NOT NULL/CHECK, exact grant delta,
Stage 0.32 preservation, business-data preservation, security/object
preservation, and health all pass. Any single failure requires ROLLBACK and
STOP. Transaction rollback is the recovery for pre-COMMIT failure.

Production DOWN is not authorized. A post-COMMIT problem requires separate
destructive rollback governance; it does not revive or extend the consumed
one-shot authority.
