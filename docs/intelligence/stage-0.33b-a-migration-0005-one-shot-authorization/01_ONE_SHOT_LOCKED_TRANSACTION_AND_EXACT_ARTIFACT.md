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

## One-shot authority and launch-attempt consumption boundary

After activation this authority permits exactly one governed production
Migration 0005 UP attempt. It is permanently consumed at the first attempt to
launch exactly:

```text
/usr/bin/docker exec -i aios-postgres \
  /usr/local/bin/psql \
  -X \
  -v ON_ERROR_STOP=1 \
  -U aios \
  -d aios
```

The launch attempt—not submission of `BEGIN;`—is the sensitive boundary. A
`docker exec` failure, failure to start `psql`, PostgreSQL connection rejection,
stdin failure, connection closure before `BEGIN;`, `BEGIN;` failure, or network/
control-plane failure permanently consumes authority. There is no automatic or
manual retry, second launch or execution, rerun after connection error, lock
timeout, verifier failure, or automatic DOWN. Any later attempt requires fresh
governance.

Before this single launch, no production `psql` connection test, `SELECT 1`, test
connection, manual `psql` probe, alternate Docker/`psql` launch, DSN probe, or
`pg_isready` through an alternate connection that creates a separate database
session is permitted. Non-database container/process metadata may be inspected
only under bounded activation checks. Repeated pre-`BEGIN` production probes are
therefore prohibited.

## Immediate pre-launch activation gates

Before the exact production control-plane launch attempt, require all of:

1. independent Stage 0.33B-A review PASS with zero blockers;
2. this authorization PR merged unchanged and Project Owner approval applicable;
3. `HEAD == main == origin/main` and a clean worktree;
4. reviewed authorization head, merge commit, and current main recorded;
5. merged Stage 0.33B-PE package present unchanged and evidence hashes exact;
6. Migration 0005 UP and DOWN hashes exact;
7. container identity and running/health metadata pass, and frozen target and
   exact control-plane argv are validated unchanged;
8. no newer governance revocation or incompatible supersession;
9. exact evidence root and one session safely provisioned and validated; and
10. `execution.jsonl` exclusively created, with initialization and
    `production_control_plane_launch_attempt` / `ATTEMPTING` records flushed and
    fsynced immediately before invoking the control plane.

Any failure before launch means DO NOT CONNECT / DO NOT EXECUTE, STOP, authority
UNCONSUMED. No pull, merge, reset, repair, restart, fallback target, or argument
substitution is implicitly authorized. An evidence session already created is
finalized as activation-blocked where practical and retained; a later separately
authorized launch uses a new session ID.

The exact evidence root is
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d`, a
real non-symlink directory owned by `aiosadmin:aiosadmin`, mode `0750`, under the
narrow filesystem-only sub-authority. The exclusively created mode-`0750`
session ID is
`stage-0.33b-d-migration-0005-YYYYMMDDTHHMMSSffffffZ-<canonical-lowercase-UUIDv4>`.
It contains only exclusively created `execution.jsonl` (UTF-8 JSON Lines, bounded
required events, mode `0640` during execution) and the exclusively created final
`manifest.json`. Critical records are flushed and fsynced; finalization performs
the prohibited-secret scan, records JSONL SHA/size/count in the bounded manifest,
fsyncs file/directory state, changes both files to `0440`, and reports the SHA-256
of the complete final manifest bytes externally. Owner/group remains
`aiosadmin:aiosadmin`; existing paths/files, symlinks, overwrite, cleanup, and
broad filesystem operations are prohibited. Provisioning failure before launch
blocks activation with authority UNCONSUMED. Post-launch evidence failure leaves
authority CONSUMED, requires fail-closed ROLLBACK if pre-COMMIT, and permits no
retry. Evidence finalization is not Stage 0.33B-V; that stage remains separately
authorized.

## Single explicit transaction and deterministic four-table locks

The future deployment must use exactly one explicit PostgreSQL transaction at
READ COMMITTED isolation and submit the locks exactly as follows:

```sql
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
LOCK TABLE public.material_receipts IN ACCESS EXCLUSIVE MODE;
LOCK TABLE public.material_receipt_items IN SHARE MODE;
LOCK TABLE public.inventory_movements IN SHARE MODE;
LOCK TABLE public.material_stock IN SHARE MODE;
```

These are L01 through L04. The immutable order is `material_receipts` →
`material_receipt_items` → `inventory_movements` → `material_stock`. Do not
dynamically sort, reorder, parallelize, substitute, omit, add, escalate, or
conditionally acquire a lock.

`public.material_receipts` requires ACCESS EXCLUSIVE because Migration 0005
performs `ALTER TABLE` on it. The other three tables are not schema targets;
SHARE blocks ordinary concurrent writer transactions taking ROW EXCLUSIVE-level
table locks while allowing bounded read/catalog verification. This grants no DDL
authority against those three tables, and they must not be altered.

Every lock operates under the same transaction-local `lock_timeout = '5s'`. No
lock receives an independent retry. If L01, L02, L03, or L04 fails or times out,
or the exact sequence cannot execute: ROLLBACK, STOP, no retry, no DOWN.
Authority remains CONSUMED because production launch already occurred.

All four locks must be successfully held before the locked fingerprint recheck
and remain continuously held through locked baseline verification, Migration
0005 execution, pre-COMMIT fingerprint/security/object verification, and COMMIT
or ROLLBACK. No release or intermediate commit is permitted.

## Locked pre-DDL gates

After L01-L04 and before DDL, all checks must pass in this exact order:

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
5. the exact governed canonical fingerprint procedure yields
   `0 / d41d8cd98f00b204e9800998ecf8427e` for each of
   `public.material_receipts`, `public.material_receipt_items`,
   `public.inventory_movements`, and `public.material_stock`; and
6. owners, roles/attributes, memberships, ADMIN OPTION, ACLs, table/column
   privileges, triggers/functions, relations, schema/extensions, and Stage 0.32
   indexes equal the reviewed structured evidence with no unexplained drift.

Any mismatch requires ROLLBACK and STOP before DDL. No synthetic actor, backfill,
repair, or state normalization is authorized.

Immediately before sending the artifact to PostgreSQL, recalculate the UP hash
and require
`7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`.
A mismatch requires ROLLBACK and STOP. Only after every locked gate passes may
the executor send the exact committed UP file without reconstruction. DOWN must
not execute.
