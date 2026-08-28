# One-Shot Migration 0005 Transaction and Verification

## Activation and consumption

The canonical sequence is **0.33B-G → 0.33B-P → 0.33B-A → 0.33B-D →
0.33B-V**: governance review and merge; separately authorized production
READ-ONLY preflight; separately reviewed and merged one-shot Migration 0005
execution authorization; exactly one controlled production Migration 0005
execution attempt; and separately authorized new-session READ-ONLY
post-deployment verification. There is no 0.33B-P → 0.33B-D shortcut.

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

After the lock and before DDL, recheck in this exact order:

1. production target identity: expected container/control-plane context,
   database `aios` owned by `aios`, current user/administrative role `aios`,
   schema `public` owned by `pg_database_owner`, relation
   `public.material_receipts` of kind `r` owned by `aios`; any other tuple
   requires ROLLBACK and return to governance;
2. creator column remains absent;
3. named creator constraint remains absent;
4. Stage 0.32 index remains present, valid, ready, unique, sole-keyed on
   `source_asset_reference`, with unchanged predicate;
5. `public.material_receipts` row count is exactly zero;
6. critical four-table counts and canonical digests match preflight;
7. relevant security/object/ACL baseline matches preflight; and
8. immediately before execution, the exact committed Migration 0005 UP artifact
   hash is
   `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`.

Only after all eight rechecks pass may the exact artifact execute. Target
identity comes first because the executor must prove it is inspecting the
intended production database, schema, and relation before interpreting any row
count or schema state. A zero-row result from the wrong target is invalid
evidence. Any target mismatch requires ROLLBACK and STOP before DDL.

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

Migration 0005 performs its transactional `ALTER TABLE` and `GRANT` inside the
same PostgreSQL transaction. If any failure occurs before COMMIT, PostgreSQL
ROLLBACK must revert both the schema changes—the
`created_by_actor_reference` column and creator CHECK—and the privilege change,
`INSERT (created_by_actor_reference)` for the candidate writer. No partial grant
may commit, and no cleanup GRANT/REVOKE script is required after a successful
transaction rollback.

The failed-attempt report must verify after rollback that the creator column is
absent, the creator constraint is absent, and candidate creator-column INSERT
privilege is absent. Any persistent partial state is **BLOCKED — RETURN TO
GOVERNANCE**. There is no retry and no production DOWN.

## Frozen execution health contract

After Migration 0005 and its structural/security verification, but before
COMMIT, bounded health evidence must prove all of the following:

- PostgreSQL responds normally; the expected production container remains
  running and healthy, with container identity, start identity/start time, and
  restart count unchanged from the execution/preflight baseline;
- the PostgreSQL process/service did not restart;
- database `aios`, schema `public`, and the fixed control-plane/administrative
  identity remain unchanged;
- `aios.service` remains in its original pre-stage state and was neither
  restarted nor activated by Stage 0.33B;
- `runtime.env` remains unchanged; and
- no candidate production traffic was activated.

Any mismatch before COMMIT requires ROLLBACK and STOP.

After a successful COMMIT, but before classifying 0.33B-D successful, bounded
operational evidence must prove the same container identity is running and
healthy, restart count is unchanged, and PostgreSQL responds normally using a
fresh bounded query/session if the execution contract requires it. It must also
prove that `aios.service` retains the same PID/start identity where applicable
and was not restarted by Stage 0.33B; `runtime.env`, Telegram, and Universal
Ingestion remain unchanged; and candidate production activation remains absent.
This immediate completion check is not the final 0.33B-V proof.

If COMMIT succeeds but this immediate post-COMMIT health check fails or is
inconclusive, classify **POST-COMMIT HEALTH VERIFICATION FAILED / INCONCLUSIVE
— RETURN TO GOVERNANCE**. Do not rerun Migration 0005 or execute DOWN; the
one-shot authority remains consumed.
