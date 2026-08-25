# Transaction, Structured Verifier, and Preservation Contract

## Attempt and transaction

The authority permits exactly one fresh attempt. After successful preflight, the
executor begins one explicit PostgreSQL transaction, applies the exact frozen up
migration, runs every structured verifier and preservation assertion, and commits
only when all gates pass. Any failure rolls back the transaction and consumes the
authority. The executor then stops; there is no same-authority retry and no down
migration execution.

No insert-based production schema test is permitted. Immediately before commit,
each new table must contain exactly zero rows.

## Structured schema verification

Verification reads independent structured catalog fields for ordinal columns,
types and UDTs, precision and scale, nullability, defaults, constraints, FK
actions, indexes, ownership, ACLs, dependencies, and non-internal triggers. It
must not depend on unsafe implicit concatenation of internal catalog types.

For `public.material_receipts`, require exact column order, types, nullability,
defaults, primary key, six-state status, supplier/document/source checks,
version/confirmation checks, the three approved indexes, zero unexpected FKs,
and zero non-internal triggers.

For `public.material_receipt_items`, require exact columns and defaults; receipt
and material-stock FKs with NO ACTION update/delete semantics;
receipt/line uniqueness; packaging, positive quantity, exact formula, colly,
unit, sheet-integrality, lifecycle, and resolved-material checks; the approved
partial material index; and zero non-internal triggers.

For `public.inventory_movements`, require exact columns and defaults; material-
stock and source-item FKs with NO ACTION semantics; source-item uniqueness;
RECEIPT-only type; positive delta; unit, actor, nonnegative balance, exact balance
formula, and sheet-integrality checks; the approved material/posting index; and
zero non-internal triggers.

## Preservation and commit gates

Before and after execution, `material_stock` must retain the same existence,
schema, constraints, indexes, ownership, ACL/grants, row count, bounded content
fingerprint, and data. `aios_material_stock_reader` must remain unchanged.

The unrelated-schema fingerprint must prove that the only new objects are the
three approved tables and their owned approved constraints and indexes. There may
be no new role, grant, trigger, function, procedure, extension, or unrelated
relation, and no ownership or default-privilege change.

Immediately before commit, require zero rows in `material_receipts`,
`material_receipt_items`, and `inventory_movements`. Any preservation, schema,
empty-table, role, grant, ownership, or object-scope mismatch forces rollback and
STOP.
