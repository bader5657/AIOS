# Stage 0.33B-A One-Shot Locked Transaction and Exact Artifact

## Exact migration artifact and allowed delta

The only production artifact eligible for future execution is the exact
committed file:

`migrations/postgres/0005_add_material_receipt_creator_provenance.up.sql`

| Artifact | Required SHA-256 | Authority |
|---|---|---|
| Migration 0005 UP | `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293` | one future attempt, subject to activation |
| Migration 0005 DOWN | `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` | identity only; NOT AUTHORIZED |

Reconstructed SQL, copy/pasted DDL, manual `ALTER TABLE`, an edited temporary
migration, extracted/modified statements, DOWN, or an alternate script is
prohibited.

Exactly three persistent changes are allowed:

1. `public.material_receipts.created_by_actor_reference TEXT NOT NULL`;
2. the exact reviewed named UUIDv4/operator CHECK implemented by Migration 0005;
3. candidate-writer column-level `INSERT(created_by_actor_reference)` privilege.

No business row, backfill, default, nullable staging state, provenance index,
trigger, function, table, owner/role/membership/ADMIN OPTION change, posting
privilege expansion, creator UPDATE privilege, reader write, stock/movement
privilege expansion, Stage 0.32 index change, or runtime activation may persist.

## One-shot authority and consumption boundary

After activation this authority permits exactly one governed production
Migration 0005 UP attempt. It is consumed when the future deployment controller
first submits the governed `BEGIN;` into the correctly launched production
PostgreSQL session. This is the sensitive execution boundary. A source,
authorization, evidence, artifact, target, retention-provisioning, or connection
failure before that first governed SQL submission leaves authority unconsumed.

Once that boundary is crossed, success, rollback, failure, connection loss,
lock timeout, verifier failure, or an inconclusive result permanently consumes
the authority. There is no automatic or manual retry, “try again,” second
execution, rerun after a connection error/lock timeout/verifier failure, or
automatic DOWN. Any later attempt requires fresh governance.

## Immediate activation gates

Before the production session may materially start, require all of the
following:

1. independent Stage 0.33B-A review PASS with zero blockers;
2. this authorization PR merged unchanged and Project Owner approval applicable;
3. `HEAD == main == origin/main` and a clean worktree;
4. the reviewed authorization head, merge commit, and current main recorded;
5. merged Stage 0.33B-PE package present unchanged and all evidence hashes exact;
6. Migration 0005 UP and DOWN hashes exact;
7. frozen target and exact control plane unchanged;
8. no newer governance revocation or incompatible supersession; and
9. a validated immutable, bounded, secret-safe Stage 0.33B-D execution-evidence
   retention destination provisioned before connection.

Any failure means DO NOT CONNECT / DO NOT EXECUTE, STOP, with authority
unconsumed. No pull, merge, reset, repair, restart, fallback target, or argument
substitution is implicitly authorized.

## Single explicit transaction

The future deployment must use exactly one explicit PostgreSQL transaction at
READ COMMITTED isolation:

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

If ACCESS EXCLUSIVE lock acquisition exceeds five seconds: ROLLBACK, STOP, no
retry, no DOWN. Because `BEGIN;` was already submitted, authority is consumed.

## Locked pre-DDL gates

After lock acquisition and before DDL, all checks must pass in this order:

1. target identity equals database/owner/user `aios`/`aios`/`aios`, schema/owner
   `public`/`pg_database_owner`, and relation/kind/owner
   `material_receipts`/`r`/`aios`;
2. creator column and exact named creator CHECK are both absent—presence is not
   idempotent success;
3. Stage 0.32 index is present, valid, ready, unique, with unchanged sole key and
   predicate; Migration 0004 must not run;
4. exact `COUNT(*)` on `public.material_receipts` is zero; a positive count
   classifies EXISTING MATERIAL RECEIPTS REQUIRE HISTORICAL PROVENANCE
   GOVERNANCE;
5. all four exact governed fingerprints freshly equal the reviewed zero/digest
   baseline; and
6. owners, roles/attributes, memberships, ADMIN OPTION, ACLs, table/column
   privileges, triggers/functions, relations, schema/extensions, and Stage 0.32
   indexes equal the reviewed structured evidence with no unexplained drift.

Any mismatch requires ROLLBACK and STOP before DDL. No synthetic actor,
backfill, repair, or state normalization is authorized.

Immediately before sending the artifact to PostgreSQL, recalculate the UP hash
and require
`7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`.
A mismatch requires ROLLBACK and STOP. Only after every locked gate passes may
the executor send the exact committed UP file without reconstruction. DOWN must
not execute.

