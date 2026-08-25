# Migration, Deployment, Rollback, and Verification Plan

## Dependency and rollback order

The future up migration assumes the preverified existence of
`public.material_stock`, then creates `material_receipts`,
`material_receipt_items`, `inventory_movements`, and the approved non-constraint
indexes in that order. Primary-key and unique-constraint indexes arise from their
constraints and are not duplicated manually.

The down migration drops `inventory_movements`, `material_receipt_items`, and
`material_receipts` in reverse dependency order. It uses explicit drops without
`CASCADE`. Table-owned indexes disappear with their tables. It must not touch
`material_stock`, `registry_records`, or another object.

The down migration is repository rollback tooling, not standing production
execution authority. Once business rows exist, any production down execution is
data-destructive and requires separate explicit data-loss governance.

## Production authority and transaction policy

Stage 0.27 does not authorize production deployment. Future eligibility requires
repository implementation, isolated PostgreSQL tests, review and merge, frozen
file hashes, separate execution authority, complete production preflight, and one
controlled attempt.

The future attempt uses one explicit PostgreSQL transaction: begin, execute the
exact hash-verified up migration, run the structured verifier, and commit only if
every assertion passes. Any failure rolls back the complete transaction. There
is no retry under the same execution authority.

## Production preflight

Before execution, evidence must establish:

- exact production identity, database `aios`, and schema `public`;
- PostgreSQL health and recorded restart count;
- exact approved `material_stock` schema and dependency availability;
- absence of all three target tables and any `0003` collision;
- exact migration hashes and approved clean-main commit;
- bounded schema, ownership, role, grant, and material-stock count/content
  fingerprints.

An unexpected target object, identifier collision, fingerprint mismatch, health
failure, or identity ambiguity is a stop condition. No automatic repair is
allowed.

## Structured verifier

Verification uses independent structured catalog fields rather than synthetic
concatenations of PostgreSQL internal type renderings. For each table it verifies
column order, types, precision/scale, nullability, defaults, primary key, exact
checks, foreign keys, unique constraints, indexes, ownership, grants, and absence
of unexpected triggers or dependencies.

For `material_receipts`, the verifier covers supplier/document/source checks,
status vocabulary, version and confirmation constraints, approved indexes, and
absence of an unexpected FK.

For `material_receipt_items`, it covers receipt and material FKs,
receipt/line uniqueness, packaging and quantity constraints, exact formula, unit
vocabulary, sheet integrality, lifecycle, resolved-material rule, and approved
material index.

For `inventory_movements`, it covers both FKs, source-item uniqueness,
RECEIPT-only type, positive delta, unit vocabulary, nonnegative balances, exact
balance formula, sheet integrality, and material/posting-history index.

Immediately before commit, each new table must contain exactly zero rows. No
production insert-based schema test is permitted.

## Preservation and isolated tests

Before/after evidence must prove unchanged `material_stock` schema, ownership,
grants, indexes, constraints, row count, bounded content fingerprint, and data.
Unrelated relations, constraints, indexes, routines, triggers, roles, grants, and
ownership must also remain unchanged.

Future isolated PostgreSQL tests cover successful up migration; exact tables,
columns, constraints, FKs, indexes, lifecycle/version rules, packaging semantics,
sheet integrality, idempotency, movement balances, absence of triggers, empty
initial tables, material-stock preservation, exact three-table down behavior,
material-stock survival, and clean recreation where applicable. Production is
not a test environment.
