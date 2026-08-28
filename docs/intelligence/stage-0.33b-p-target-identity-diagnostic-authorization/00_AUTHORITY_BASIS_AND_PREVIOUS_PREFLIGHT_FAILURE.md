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
diagnostic session using only D01 and D02 after this package receives independent
review PASS and is merged unchanged. Before those conditions, authority is
inactive.

The Project Owner does not authorize a full preflight rerun, Migration 0005 or
0004, DDL, DML, locks, ownership changes, role/grant/membership changes, repair,
retry, service restart, runtime changes, external-integration changes, or
production candidate activation.

