# Stage 0.33B-VR R03 Actual/Expected Diff and PostgreSQL Semantics

Date: 2026-08-29 (Asia/Jakarta)

## Exact retained R03 evidence

The retained record binds `query_id=R03`, `frame_id=R03`, field count `5`, row
count `36`, status `FAIL`, semantic assertion `semantic mismatch`, and payload
SHA-256 `8117c7ea1b355d96076c38ff9a15a00d1d5da128273f50fce2869b54106015a8`.

The five fields are, in order:

`grantee, table_schema, table_name, privilege_type, is_grantable`.

The actual ordered payload consists exactly of:

1. For grantee `aios`, schema `public`, each table in
   `inventory_movements`, `material_receipt_items`, `material_receipts`,
   `material_stock`, and each privilege in `DELETE`, `INSERT`, `REFERENCES`,
   `SELECT`, `TRIGGER`, `TRUNCATE`, `UPDATE`: one tuple with
   `is_grantable=YES` (28 tuples).
2. `aios_material_inventory_posting_writer`: `SELECT/NO` on each of the four
   governed tables (4 tuples).
3. `aios_material_receipt_candidate_writer`: `SELECT/NO` on
   `material_receipt_items`, `material_receipts`, and `material_stock`
   (3 tuples).
4. `aios_material_stock_reader`: `SELECT/NO` on `material_stock` (1 tuple).

No candidate/posting runtime row, PUBLIC row, write row for the stock reader,
or table-level non-owner INSERT/UPDATE row appears.

## Exact reviewed SQL contract

```sql
SELECT g.grantee, g.table_schema, g.table_name,
       g.privilege_type, g.is_grantable
FROM information_schema.role_table_grants AS g
WHERE g.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND g.table_schema = 'public'
  AND g.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY g.grantee, g.table_name, g.privilege_type;
```

The PR #251 and PR #254 R03 bodies are byte-identical: 623 bytes, SHA-256
`15fb4a909363e65a8702ca97823a142ae5a737f900db32ffda69500d8a137f41`.
PR #254 specifies a five-field complete ordered snapshot. The pre-Stage-V
execution manifest records exactly 36 bounded R03 rows. PR #251 also requires
the post-migration `PR03` payload to equal the pre-migration `R03` payload;
Migration 0005 has no table-level R03 delta.

## Failed semantic expectation and exact diff

The Stage V execution validator required all 36 scoped R03 tuples to have
`is_grantable=NO`. It separately applied non-owner update/reader-write
guardrails. That global `NO` requirement was not the reviewed SQL and conflicts
with the repository's documented owner-derived representation.

Against the validator's effective expected tuples:

- Equal rows: the eight non-owner `SELECT/NO` tuples listed above.
- Expected-only: the 28 Cartesian-product owner tuples
  `("aios","public",TABLE,PRIVILEGE,"NO")`, where `TABLE` is each of the four
  governed tables and `PRIVILEGE` is each of the seven privileges listed above.
- Actual-only: the corresponding 28 tuples
  `("aios","public",TABLE,PRIVILEGE,"YES")`.
- Field-level differences: exactly 28 differences, all confined to field 5,
  `is_grantable`, expected `NO`, actual `YES`. Fields 1-4 are equal for every
  paired owner tuple. There are no other tuple differences.

This is a complete tuple comparison over the closed role/table scope; no
substring filtering or normalization was used.

## Privilege semantics

`aios` owns all four tables, as independently retained by passing O04.
PostgreSQL represents the owner's inherent grant capability in
`information_schema.role_table_grants` with `is_grantable=YES`. Repository
disposable validation already distinguishes deterministic owner-derived rows
from ACL mutations; it explicitly says such rows are not grant deltas.

The eight `NO` tuples are the governed non-owner table SELECT grants. R02
retains exactly the candidate-runtime-to-candidate-writer and
posting-runtime-to-posting-writer memberships with no ADMIN OPTION. Those
memberships explain effective runtime access but add no runtime-grantee rows to
this retained `role_table_grants` payload. No PUBLIC row is present. Nothing in
R03 evidences a default-privilege change.

Migration 0005 granted only column-level
`INSERT(created_by_actor_reference)` to the candidate writer. That delta belongs
to R04/V05, not R03, and cannot produce any of the 28 owner table rows or alter
their `is_grantable` values. The R03 result is representation-only relative to
Migration 0005.

