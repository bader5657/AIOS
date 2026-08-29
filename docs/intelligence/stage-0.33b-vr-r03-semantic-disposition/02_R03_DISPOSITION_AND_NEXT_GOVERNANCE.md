# Stage 0.33B-VR R03 Disposition and Next Governance

Date: 2026-08-29 (Asia/Jakarta)

## Disposition

`STAGE 0.33B-VR R03 GOVERNANCE EXPECTATION DEFECT IDENTIFIED`

The retained production payload matches the documented 36-row pre-Stage-V
baseline shape and PostgreSQL owner semantics. The query is correctly bounded
and faithfully exposes both the grantee and `is_grantable`. The failure was
caused by the Stage V executor's semantic expectation that every R03 row have
`is_grantable=NO`, incorrectly including owner-derived `aios` rows.

This is not real production privilege drift. It is not a defect in the R03 SQL
representation. No production repair is required or authorized.

## Corrected exact R03 contract

A future independently reviewed validator must require exactly 36 ordered
five-field tuples:

1. 28 `aios/public/TABLE/PRIVILEGE/YES` owner tuples: all combinations of the
   four governed tables and `DELETE`, `INSERT`, `REFERENCES`, `SELECT`,
   `TRIGGER`, `TRUNCATE`, `UPDATE`;
2. four `aios_material_inventory_posting_writer/public/TABLE/SELECT/NO`
   tuples, one per governed table;
3. three `aios_material_receipt_candidate_writer/public/TABLE/SELECT/NO`
   tuples for `material_receipt_items`, `material_receipts`, and
   `material_stock`; and
4. one `aios_material_stock_reader/public/material_stock/SELECT/NO` tuple.

Ordering remains exactly `grantee, table_name, privilege_type`. No other row,
duplicate, omission, field value, runtime-grantee row, PUBLIC row, or
table-level non-owner write privilege passes. R04/V05 remain responsible for
the independently governed column-level creator INSERT assertion.

## Historical and operational state

The original Stage 0.33B-V result remains `CURRENT-STATE VERIFICATION FAILED`
under its then-executed validator. It is not retroactively changed to PASS.
Its authority remains permanently consumed and permits no retry. Any future
read-only verification requires a separately published and independently
reviewed authority after this correction is reviewed.

The valid retained I01/I02, S01, F01-F04, O01-O08, R01, and R02 observations
remain preserved. R04, V01-V05, and N01 were not reached. Stage 0.33B-D
historical semantic evidence remains permanently incomplete.

The actor-provenance operational gate remains `OPEN`. Production candidate
activation remains `NOT AUTHORIZED`. This package performs no gate closure,
production mutation, privilege repair, migration, runtime change, or
activation.

