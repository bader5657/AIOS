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

The companion `03_R04_EXACT_342_TUPLE_MANIFEST.json` explicitly enumerates all
48 `public` table/column identities in R04 SQL sort order, with stable ordinals.
It contains no external-reference placeholder. For every enumerated identity,
the four owner tuples above are required once.

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

The manifest explicitly lists every identity ordinal used by every candidate,
posting, and reader generation rule. The contract rejects any row not produced
by those self-contained enumerations.

The canonical manifest is UTF-8, sorted-key compact JSON using separators
`,` and `:`, with exactly one terminal LF. It is 7829 bytes and has SHA-256
`4f10acdff3da6e127f221356ebed7df0415668aad63d92ab04c79ab1ed92b183`.
Its derived sequence is a compact UTF-8 JSON array of ordered six-string arrays,
the same separators, `ensure_ascii=false`, and one terminal LF. The exact
342-row sequence SHA-256 is
`d7948ce205298443c814d8c26faa9303492e019cef528da0940eba5616c3db3f`.
Sequence order is exactly `grantee, table_name, column_name, privilege_type`,
matching R04 SQL; schema and grantability remain compared fields.

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

