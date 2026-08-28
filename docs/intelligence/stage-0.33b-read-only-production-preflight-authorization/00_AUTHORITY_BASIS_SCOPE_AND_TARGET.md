# Stage 0.33B-P Authority Basis, Scope, and Target

Date: 2026-08-28 (Asia/Jakarta)

## Publication boundary and source gate

This documentation-only package authorizes no production activity by its
publication or merge. During publication, production PostgreSQL is not
contacted; no production SELECT, preflight, migration, DDL, DML, table lock,
role/grant change, service or container action, credential operation, runtime
change, external integration change, model invocation, or traffic activation
is performed.

Stage 0.33A is merged and verified. Stage 0.33B-G passed final review and was
merged through PR `#243`; the reviewed governance head is
`1d3c775dbd8c1f750dc39f3178d8afe5614a9fc3`, and its merge/current-main
baseline is `797100d8d617d347909f9e130c8481ce4dcd01af`.

Before publication, repository-only evidence must prove a clean synchronized
`HEAD == main == origin/main`, including that baseline. The committed migration
inventory is 0001 through 0005. Migration 0004 was deployed once and must not be
executed again. The frozen Migration 0005 artifacts are:

| Artifact | Frozen value |
|---|---|
| UP path | `migrations/postgres/0005_add_material_receipt_creator_provenance.up.sql` |
| UP SHA-256 | `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293` |
| DOWN SHA-256 | `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` |

Any source or hash drift blocks publication. These hashes must be reconfirmed
again as an activation condition; this package does not execute either file.

## Consumed historical authority

The one Stage 0.33B-P session authorized through PR `#244` materially started,
was BLOCKED under the then-frozen owner expectation, and is permanently
consumed. Correcting the owner interpretation in this document does not
reactivate or replace that authority. A new, separately reviewed and merged
Stage 0.33B-P authorization is required before any full preflight rerun.

## Exact future authority

After every activation condition below is satisfied, the Project Owner approves
exactly one bounded Stage 0.33B-P production PostgreSQL session. Its sole purpose
is to determine whether production is eligible to request the separately
reviewed Stage 0.33B-A one-shot Migration 0005 execution authorization.

The session is READ ONLY and must make zero persistent changes. A PASS grants no
DDL or migration authority. The canonical stage sequence remains:

**0.33B-G → 0.33B-P → 0.33B-A → 0.33B-D → 0.33B-V**.

The one canonical SQL bundle has this exact physical and declared order:
prefix → target identity → Migration 0005 absence → Stage 0.32 index → zero-row
→ four fingerprints → structural/schema/object snapshot → role/membership/ACL
snapshot → transaction close. No alternate ordering or runtime addition is
authorized.

P and A must not be combined or skipped.

## Frozen production target and control plane

| Target field | Required identity |
|---|---|
| Container | `aios-postgres` |
| Image family | `postgres:17-alpine` |
| PostgreSQL | `17.x` |
| Database | `aios` |
| Session user | `aios` |
| Schema | `public` |
| Primary relation | `public.material_receipts` |
| Expected database owner | `aios` |
| Expected `public` schema owner | `pg_database_owner` |
| Expected primary-relation owner | `aios` |
| Expected primary-relation kind | `r` (ordinary table) |

This exact tuple is target-specific and fail-closed. PostgreSQL predefined role
`pg_database_owner` owns the governed `public` schema and represents the current
database owner through PostgreSQL's predefined-role semantics. Its literal role
name need not equal the database owner's role name. No other owner tuple is
accepted, and no ownership mutation is authorized.

The only authorized control plane is this fixed argv shape:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

Only the exact ordered governed query bundle frozen in this package may be
supplied through stdin. Ad-hoc/exploratory SQL, runtime additions, arbitrary
SELECT/function calls, non-allowlisted functions, and dynamic SQL are prohibited.
Every psql backslash/meta-command is prohibited, including `\gexec`, `\copy`,
and `\!`; the bundle has zero line-leading backslash commands. Host PostgreSQL
or host `psql` fallback, credential-bearing URI/DSN, external endpoint, arbitrary
container, database, or user is prohibited. Credentials, connection strings,
and secrets must not appear in argv, logs, or evidence.

## Activation conditions

This one-session authority becomes ACTIVE only after all of the following:

1. this authorization PR receives independent review PASS with zero blocking
   findings;
2. the authorization PR is merged unchanged;
3. Project Owner approval recorded here remains applicable;
4. `HEAD == main == origin/main` and the worktree is clean;
5. both Migration 0005 hashes are reconfirmed exactly; and
6. the frozen production target and control-plane contract is unchanged.

Before activation, production preflight remains not authorized. Failure or
inconclusive proof of any condition keeps authority inactive.

## Project Owner approval and exclusions

The Project Owner approves exactly one bounded READ-ONLY production preflight
session on the fixed governed target for eligibility assessment only, subject
to activation conditions. The Project Owner does **not** authorize Migration
0005 or 0004 execution, DDL, DML, `LOCK TABLE`, GRANT, REVOKE, DOWN, retry,
repair, credential rotation, service/container restart, candidate activation,
Telegram or Universal Ingestion changes, confirmation, or posting.
