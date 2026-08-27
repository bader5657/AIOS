# Stage 0.32 Migration 0004 — One-Shot Production Execution Authorization

Date: 2026-08-27 (Asia/Jakarta)

## Publication boundary

This documentation-only package records a proposed authority for exactly one
future production Migration 0004 execution attempt. Creating, reviewing, or
merging it executes no production query or mutation. The authority remains
inactive until all activation conditions below pass.

## Frozen basis and preflight evidence

| Control | Frozen value |
|---|---|
| Stage 0.32 implementation | Merged and verified |
| Migration governance | PR `#236`, merged and verified |
| Governance reviewed head | `b71a0e3e9403c5131adc4354803b2b28de91779b` |
| Governance merge baseline | `c112be5ee24b08f1fe1a210ef6675ba55ac31c23` |
| Read-only preflight authority | Consumed |
| Preflight classification | **PRODUCTION DUPLICATE PREFLIGHT PASS — ZERO ACTIVE DUPLICATE SOURCES — ELIGIBLE FOR MIGRATION 0004 EXECUTION AUTHORIZATION** |
| Active duplicate groups | `0` |
| Migration 0004 | Not executed |

The successful preflight recorded container `aios-postgres`, image
`postgres:17-alpine`, PostgreSQL 17.10, database/user `aios`, schema `public`, a
running healthy container with restart count zero, all four required tables,
and the required Migration 0002/0003 schema baseline. The new index was absent;
`material_receipts_source_asset_idx` was present, non-unique, and keyed solely
by `source_asset_reference`.

The canonical pre-authorization business evidence was:

| Table | Row count | Row digest |
|---|---:|---|
| `public.material_receipts` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.material_receipt_items` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.inventory_movements` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.material_stock` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |

These values are continuity gates, not a substitute for a fresh locked
before-DDL baseline. Any pre-execution count or digest drift blocks mutation and
requires a new read-only preflight and governance decision.

## Frozen artifact and target

| Control | Frozen value |
|---|---|
| UP path | `migrations/postgres/0004_add_material_receipt_source_active_uniqueness.up.sql` |
| UP SHA-256 | `90a009a33d4ca1cfcb3bd9b68170188f46626edc6789fba27f60c7b96f684baf` |
| DOWN path | `migrations/postgres/0004_add_material_receipt_source_active_uniqueness.down.sql` |
| DOWN SHA-256 | `4a702755c855c55f0300b9f57d8aa290846d413d2c7de88cb728f5e490225977` |
| Container / image | `aios-postgres` / `postgres:17-alpine` |
| Database / admin identity | `aios` / `aios` |
| Schema / table | `public` / `public.material_receipts` |
| Existing index retained | `public.material_receipts_source_asset_idx` |
| Authorized new object | `public.material_receipts_source_asset_active_uidx` |

The only approved UP semantics are:

```sql
CREATE UNIQUE INDEX material_receipts_source_asset_active_uidx
ON material_receipts (source_asset_reference)
WHERE status NOT IN ('REJECTED', 'CANCELLED');
```

Execution must consume the exact frozen UP file. Reconstructed SQL,
`IF NOT EXISTS`, `CONCURRENTLY`, `CASCADE`, additional DDL, DOWN, role/grant
statements, and business-data mutation are unauthorized.

The fixed control plane is:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

SQL is supplied through approved stdin/file input. Host PostgreSQL, host socket,
`sudo -u postgres`, external endpoints, caller-selected targets/identities, and
password-bearing argv or URI forms are prohibited.

## Authority scope and activation

The sole authorized future mutation is creation of the one frozen index. There
is no authority for data reconciliation, INSERT/UPDATE/DELETE, candidate
creation, movements, stock mutation, roles, grants, ownership, credentials,
runtime changes, restart, Telegram, Universal Ingestion, confirmation, posting,
actor provenance, candidate activation, or DOWN.

The authority becomes **ACTIVE** only after:

1. this authorization PR receives an independent review with zero blockers;
2. the PR is merged without reviewed-head drift;
3. explicit Project Owner approval for exactly one attempt is recorded;
4. clean synchronized `HEAD == main == origin/main` is established;
5. both migration hashes are reverified; and
6. every pre-execution source, target, health, identity, index, schema,
   continuity, and safety gate passes.

Until then: **MIGRATION 0004 ONE-SHOT EXECUTION AUTHORITY: INACTIVE**.

## Project Owner approval record

**Status: APPROVED, CONDITIONALLY DORMANT UNTIL ALL ACTIVATION CONDITIONS PASS.**

The Project Owner approval conveyed for this authorization package is recorded
with this exact narrow scope:

> Approve exactly one future production Migration 0004 UP execution attempt,
> only after independent authorization review, merge, and every frozen
> pre-execution gate passes. No data reconciliation, DOWN migration,
> credential, role/grant, runtime, activation, Telegram, posting, confirmation,
> or actor-provenance authority is granted.

The approval record must remain attached to the independently reviewed PR or an
equivalent governed record. It does not bypass review, merge, source/hash, or
pre-execution safety gates and grants no authority during package publication.
