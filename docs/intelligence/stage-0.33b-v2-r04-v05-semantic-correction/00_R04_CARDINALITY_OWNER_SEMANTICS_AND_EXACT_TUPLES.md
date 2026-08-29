# Stage 0.33B-V2C R04 Exact Column-Privilege Contract

Date: 2026-08-29 (Asia/Jakarta)

## Existing SQL and result shape

R04 remains the unchanged PR #251/PR #254 query over
`information_schema.column_privileges`. It selects, in order, `grantee`,
`table_schema`, `table_name`, `column_name`, `privilege_type`, and
`is_grantable`; it closes scope to the six governed roles, `public`, and the
four governed tables, ordered by grantee, table, column, and privilege.

PostgreSQL 17.10 disposable validation returned exactly 342 distinct six-field
rows in that order:

- 192 `aios` owner-derived rows: for every one of the 48 governed columns,
  exactly `INSERT`, `REFERENCES`, `SELECT`, and `UPDATE`, each with
  `is_grantable=YES`;
- 80 candidate-writer rows, all `is_grantable=NO`;
- 64 posting-writer rows, all `is_grantable=NO`;
- 6 stock-reader `material_stock` `SELECT/NO` rows; and
- zero PUBLIC, runtime-role, or other rows.

The four owner creator-column tuples are exactly
`aios/public/material_receipts/created_by_actor_reference/PRIVILEGE/YES` for
`PRIVILEGE` in `INSERT`, `REFERENCES`, `SELECT`, `UPDATE`. These are owner
representation, not direct ACL mutations.

## Complete closed tuple generator

The exact 342-row set is frozen without wildcard acceptance as follows.

The governed columns are the exact 48-column post-0005 schema: 14
`material_receipts`, 16 `material_receipt_items`, 12 `inventory_movements`, and
6 `material_stock` columns in O01 ordinal order. For each column, the four
owner tuples above are required once.

Non-owner tuples are required once for each exact grant:

- candidate writer: table-derived SELECT on all 14 receipt, 16 item, and 6
  stock columns; INSERT on the seven receipt columns including
  `created_by_actor_reference`; UPDATE on the eleven governed receipt columns;
  INSERT on the thirteen governed item columns; UPDATE on the thirteen governed
  item columns;
- posting writer: table-derived SELECT on all 48 columns; UPDATE on
  `status,updated_at` for receipts and items; INSERT on the ten governed
  movement columns; UPDATE on `stock_qty,updated_at`; and
- stock reader: table-derived SELECT on all six stock columns.

The exact column lists are those frozen by the merged writer privilege matrix
and schema migrations; ordering is the SQL ORDER BY, not grant order. The
contract rejects any row not produced by these enumerations.

## 340-to-342 defect

The old 340 calculation added only four new owner creator rows plus the direct
candidate creator INSERT row to the 335-row pre-0005 snapshot. It omitted two
deterministic rows caused by existing table SELECT grants applying to the new
column:

1. `aios_material_inventory_posting_writer/public/material_receipts/created_by_actor_reference/SELECT/NO`;
2. `aios_material_receipt_candidate_writer/public/material_receipts/created_by_actor_reference/SELECT/NO`.

These two rows fully explain the cardinality delta. Missing, extra, duplicate,
wrong-field, PUBLIC, runtime-role, wrong-grantability, or unauthorized
non-owner-write tuples fail.

