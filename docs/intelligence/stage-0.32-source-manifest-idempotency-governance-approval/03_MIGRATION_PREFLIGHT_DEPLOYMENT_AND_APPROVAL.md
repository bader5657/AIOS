# Stage 0.32 Migration, Preflight, Deployment, and Activation Boundary

## Migration identity

The next migration number is `0004`, subject to independent re-verification
before implementation. The expected paths are:

```text
migrations/postgres/0004_add_material_receipt_source_active_uniqueness.up.sql
migrations/postgres/0004_add_material_receipt_source_active_uniqueness.down.sql
```

The up migration contains only the approved partial unique index. The down
migration removes only `material_receipts_source_asset_active_uidx`, without
`CASCADE`, data deletion, status mutation, unrelated index removal, or rewriting.

No role/grant, actor-provenance, schema-column, or unrelated migration change is
authorized.

## Production duplicate preflight

Before any future production migration, execute a read-only structured query
equivalent to:

```sql
SELECT
    source_asset_reference,
    COUNT(*) AS active_count,
    ARRAY_AGG(receipt_id ORDER BY receipt_id) AS receipt_ids,
    ARRAY_AGG(status ORDER BY receipt_id) AS statuses
FROM material_receipts
WHERE status NOT IN ('REJECTED', 'CANCELLED')
GROUP BY source_asset_reference
HAVING COUNT(*) > 1;
```

Any returned row is a HARD STOP. Do not choose a winner, delete, cancel, reject,
mutate, or create the index. Require separately governed reconciliation.
Evidence may contain only bounded identifiers needed for reconciliation; never
credentials, DSNs, unnecessary document contents, or unrelated rows.

No production preflight is authorized by this package.

## Candidate privilege boundary

The existing runtime identity remains
`aios_material_receipt_candidate_runtime`. No new privilege is expected or
authorized: no DDL, ownership, schema administration, stock write, movement
insert, posting role, or admin role.

## Deployment and gate closure

The required sequence is:

1. merge this governance approval;
2. issue separate migration/repository implementation authority;
3. implement and independently review the migration and duplicate mapping;
4. merge the implementation;
5. obtain separate production migration authority;
6. run the read-only duplicate preflight;
7. execute one controlled production migration;
8. perform post-deployment verification.

Only after all of those steps may the source-manifest idempotency gate be
declared operationally closed. Governance approval or repository implementation
alone does not close it.

Remaining activation gates are durable candidate-creation actor provenance,
runtime-secret/activation safety, and explicit production safety review.

## Exclusions and safety

Telegram and Universal Ingestion remain unchanged. No automatic candidate wiring,
service startup, event-router wiring, OCR, Vision, LLM, Brain, production
traffic, credential creation, or production PostgreSQL access is authorized.

## Project Owner approval

The Project Owner APPROVES this Stage 0.32 boundary, invariant, partial-index
strategy, duplicate outcome, preflight stop policy, test obligations, migration
plan, and activation sequencing. This approval authorizes a later, separate
implementation decision only; it does not authorize implementation, deployment,
or production activation.

`STAGE 0.32 SOURCE-MANIFEST CANDIDATE IDEMPOTENCY GOVERNANCE APPROVED — READY FOR MIGRATION / REPOSITORY IMPLEMENTATION AUTHORIZATION`

