# Stage 0.32 Post-Deployment Verification Authorization

Date: 2026-08-27 (Asia/Jakarta)

## Publication boundary

This documentation-only package proposes exactly one future bounded READ-ONLY
production post-deployment verification session. Creating, reviewing, or
merging it contacts no production database and grants no mutation authority.
Migration 0004 must not be executed again; DOWN remains unauthorized.

## Frozen authority and execution basis

| Control | Frozen result |
|---|---|
| Stage 0.32 implementation | Merged and verified |
| Production migration governance | PR `#236`, merged and verified |
| Production duplicate preflight | PASS — zero active duplicate sources |
| Migration execution authorization | PR `#237`, merged and active before execution |
| Authorization merge commit | `131c9cde09e8dc93c203d4a211ee869a859a2ad6` |
| Migration execution | **MIGRATION 0004 DEPLOYED AND VERIFIED — ONE-SHOT AUTHORITY CONSUMED — POST-DEPLOYMENT VERIFICATION STILL REQUIRED** |
| Execution authority | CONSUMED; no second attempt |

The execution completed one exact hash-bound UP attempt and COMMIT. The
transaction reported zero locked active-duplicate groups, exact new-index
structure, preservation of the existing source index, unchanged four-table
counts/digests, and identical bounded before/after security/object digests.

## Frozen production and artifact baseline

| Control | Frozen value |
|---|---|
| Container / image | `aios-postgres` / `postgres:17-alpine` |
| PostgreSQL | 17.10 |
| Database / administrative identity | `aios` / `aios` |
| Schema / target table | `public` / `public.material_receipts` |
| Health after execution | running / healthy |
| Container restart count | 0 |
| UP path | `migrations/postgres/0004_add_material_receipt_source_active_uniqueness.up.sql` |
| UP SHA-256 | `90a009a33d4ca1cfcb3bd9b68170188f46626edc6789fba27f60c7b96f684baf` |
| DOWN SHA-256 | `4a702755c855c55f0300b9f57d8aa290846d413d2c7de88cb728f5e490225977` |
| UP state | deployed once |
| DOWN state | not executed / not authorized |

Runtime service state, `runtime.env`, Telegram, and Universal Ingestion were
unchanged. Candidate, confirmation, and posting activation did not occur.

## Strict scope and activation

The sole proposed authority is one explicit READ-ONLY transaction containing
identity, index/catalog, duplicate, canonical fingerprint, and bounded
security/object SELECTs, followed by read-only container/service/file-metadata
checks. It grants no `CREATE`, `DROP`, `ALTER`, `INSERT`, `UPDATE`, `DELETE`,
`TRUNCATE`, lock, role/grant/ownership, credential, configuration, restart,
runtime, reconciliation, activation, UP, or DOWN authority.

The verification authority becomes active only after:

1. this authorization PR receives independent review with zero blockers;
2. its exact reviewed head merges without drift;
3. the conditional Project Owner approval below remains recorded;
4. clean synchronized `HEAD == main == origin/main` is established; and
5. the migration hashes and fixed read-only target/control plane are reverified.

Until then: **POST-DEPLOYMENT READ-ONLY VERIFICATION AUTHORITY: INACTIVE**.

## Project Owner approval record

**Status: APPROVED, CONDITIONALLY DORMANT UNTIL ALL ACTIVATION CONDITIONS PASS.**

> Approve exactly one bounded production post-deployment verification session,
> using one READ-ONLY PostgreSQL transaction and bounded external metadata
> checks. No migration, lock, corrective mutation, DOWN, role/grant, credential,
> runtime, Telegram, ingestion, posting, confirmation, actor-provenance, or
> candidate-activation authority is granted.

This approval does not bypass independent review, merge, source synchronization,
hash verification, or any fail-closed identity/safety gate.
