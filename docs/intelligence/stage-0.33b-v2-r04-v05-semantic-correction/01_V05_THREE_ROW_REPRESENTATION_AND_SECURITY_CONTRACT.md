# Stage 0.33B-V2C V05 Three-Row Security Contract

Date: 2026-08-29 (Asia/Jakarta)

## Unchanged query and exact output

V05 remains unchanged. It selects the same six fields from
`information_schema.column_privileges`, restricted to the four frozen
non-owner roles, `public.material_receipts`, and
`created_by_actor_reference`, ordered by grantee and privilege.

PostgreSQL 17.10 returned exactly these three ordered tuples:

1. `aios_material_inventory_posting_writer,public,material_receipts,created_by_actor_reference,SELECT,NO`
2. `aios_material_receipt_candidate_writer,public,material_receipts,created_by_actor_reference,INSERT,NO`
3. `aios_material_receipt_candidate_writer,public,material_receipts,created_by_actor_reference,SELECT,NO`

Cardinality is exactly 3, field count exactly 6, and multiplicity exactly one
for each tuple. No other tuple passes.

## Representation and semantic intent

`information_schema.column_privileges` includes a table-level privilege for
each affected column. The two SELECT rows therefore represent existing table
SELECT grants; they are not direct column SELECT ACLs. The candidate INSERT row
is the governed direct column grant. This query does not by itself distinguish
the ACL source and must not be called a direct-ACL-only verifier.

Its corrected semantic intent is a closed non-owner creator-column security
snapshot. It proves the candidate INSERT is present, candidate creator UPDATE
is absent, posting creator UPDATE is absent, the reader has no creator row, and
no unexpected non-owner write exists. Governed SELECT representation is
accepted only through the two exact tuples above, never through normalization
or a wildcard.

The V05 three rows are an exact subset of R04. Candidate INSERT and both SELECT
rows match field-for-field, including `NO`; owner rows remain outside V05's
non-owner filter and are not mistaken for ACL mutations.

