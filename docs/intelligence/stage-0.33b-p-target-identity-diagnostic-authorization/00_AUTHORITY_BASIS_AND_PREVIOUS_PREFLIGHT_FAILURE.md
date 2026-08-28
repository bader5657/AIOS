# Stage 0.33B-PD Authority Basis and Previous Preflight Failure

Date: 2026-08-28 (Asia/Jakarta)

## Publication boundary

This is a governance and authorization publication only. Publication does not
contact production PostgreSQL, execute a production SELECT, rerun Stage 0.33B-P,
execute Migration 0005 or 0004, or perform DDL, DML, `LOCK TABLE`, ownership,
role, grant, runtime, service, Telegram, Universal Ingestion, or candidate
activation work.

## Previous authority and immutable classification

Stage 0.33B-P was authorized by PR `#244` at reviewed head
`2de51be244a0e85c868664e391bf58f984887857` and merged as
`ad3dbde71ccf04375cec547e70cc5dc151b2071b`. Its exactly one authorized
production session materially started. That authority is permanently
**CONSUMED** and this package does not resurrect it.

The preflight stopped after P01-P05 and I01-I02, before M01-M02, S01, Z01,
F01-F04, O01-O08, and R01-R04. Migration 0005 pre-state and production row
counts were not queried. No migration or production mutation occurred. The
classification remains exactly:

```text
PRODUCTION ACTOR-PROVENANCE PREFLIGHT BLOCKED
— TARGET OWNERSHIP OR RELATION IDENTITY MISMATCH
```

The exact differing I02 field is unknown and must not be inferred as fact.

## Purpose and bounded hypothesis

Stage 0.33B-PD authorizes one future observation-only diagnostic session solely
to retain the exact target identity and database/schema/relation ownership
values represented by former I01 and I02. It is not a Stage 0.33B-P rerun,
deployment preflight, migration authority, repair authority, or ownership-change
authority.

The following is a hypothesis only: on modern PostgreSQL installations,
`public` may be owned by special role `pg_database_owner` while database `aios`
is owned by `aios`. The prior direct `schema_owner = 'aios'` expectation may
therefore be defective. Production evidence must establish the actual values
before governance changes. No ownership value is accepted here as fact.

## Frozen production target and control plane

| Target field | Frozen value |
|---|---|
| Container | `aios-postgres` |
| Image family | `postgres:17-alpine` |
| PostgreSQL | `17.x` |
| Database | `aios` |
| Session user | `aios` |
| Schema | `public` |
| Relation | `public.material_receipts` |

The only authorized control plane is:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

The exact bundle is supplied through stdin. Host PostgreSQL, a DSN, an alternate
container, database, user, endpoint, or control plane is prohibited.

## Activation and Project Owner approval

The Project Owner approves exactly one future bounded READ-ONLY target-identity
diagnostic session using only D01 and D02. The authority becomes ACTIVE only
when every condition below is proved immediately before the session:

1. PR `#245` received independent review PASS with zero blocking findings;
2. PR `#245` was merged unchanged;
3. Project Owner approval recorded here remains applicable;
4. `HEAD == main == origin/main` and the worktree is clean;
5. the exact reviewed PR head and authorization merge commit are recorded, and
   current `main` contains that reviewed authorization content unchanged;
6. the frozen production target is unchanged;
7. the frozen control-plane argv and stdin-only SQL transport are unchanged;
8. the previous Stage 0.33B-P authority remains recorded as consumed; and
9. no newer governance has revoked or incompatibly superseded this authority.

The executor must perform this fresh source, authorization-content, target, and
control-plane gate immediately before production connection, not merely during
publication. Before all conditions pass, authority is inactive and unconsumed.

Source proof requires the expected branch with `HEAD == main`,
`main == origin/main`, therefore `HEAD == main == origin/main`, and no modified,
staged, untracked, or otherwise uncommitted worktree content. Record the reviewed
PR head, authorization merge commit, and current-main commit before the session.

The target/control-plane gate may inspect only bounded, non-secret, non-mutating
metadata sufficient to prove that `aios-postgres` exists and is running, its
image remains in the `postgres:17-alpine` family, the fixed binary paths remain
expected, and no container, database, user, or argv parameter was substituted.
Do not contact PostgreSQL for this gate when the facts can be established
without doing so. D01 remains the first database-side identity verification.

If source identity cannot be proved, the worktree is dirty, an unexpected branch
is checked out, `origin/main` advanced, authorization content drifted, or newer
governance superseded the authority: do not connect, authority remains
unconsumed, STOP, and return to governance/operator control. Do not automatically
pull, merge, rebase, reset, clean, or resolve conflicts to make the gate pass.

If any frozen target or control-plane value differs, do not connect and classify:

```text
STAGE 0.33B-PD AUTHORITY ACTIVATION BLOCKED
— FROZEN PRODUCTION TARGET OR CONTROL-PLANE CONTRACT DRIFT
```

Authority remains unconsumed. No alternate target, fallback, container/image or
database recreation, service restart, or automatic repair is authorized.

The Project Owner does not authorize a full preflight rerun, Migration 0005 or
0004, DDL, DML, locks, ownership changes, role/grant/membership changes, repair,
retry, service restart, runtime changes, external-integration changes, or
production candidate activation.

