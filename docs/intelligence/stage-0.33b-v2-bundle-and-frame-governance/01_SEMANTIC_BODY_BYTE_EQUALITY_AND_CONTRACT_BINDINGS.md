# Stage 0.33B-V2P Semantic Equality and Corrected Contract Bindings

Date: 2026-08-29 (Asia/Jakarta)

## Mechanical byte-identity result

The V2 bundle was produced from the exact historical Stage V bytes by replacing
only the 36-byte old frame nonce with the 36-byte frozen V2 frame nonce. A
mechanical inverse replacement reproduces the historical bundle byte-for-byte,
including comments, whitespace, transaction control, query order, field order,
filters, and ordering clauses. The complete executable diff is therefore the
26 frame nonce string literals. No semantic SQL token changed.

Exact statement extraction and byte comparison passed 25/25 for
`I01,I02,S01,F01,F02,F03,F04,O01,O02,O03,O04,O05,O06,O07,O08,R01,R02,R03,R04,V01,V02,V03,V04,V05,N01`.
Frame IDs, structure, positions, and field counts are unchanged. R04 and V05
SQL bodies are byte-identical to historical Stage V; only their reviewed
expected-result contracts are corrected.

## R03 binding

PR #256's closed five-field R03 contract is exactly 36 rows: 28 owner-derived
`aios` rows with `is_grantable=YES`, and eight governed non-owner `SELECT/NO`
rows. No wildcard or normalization is accepted.

## R04 binding

PR #257's self-contained manifest is
`docs/intelligence/stage-0.33b-v2-r04-v05-semantic-correction/03_R04_EXACT_342_TUPLE_MANIFEST.json`.
Its raw-byte SHA-256 is
`4f10acdff3da6e127f221356ebed7df0415668aad63d92ab04c79ab1ed92b183`,
and its canonical ordered tuple SHA-256 is
`d7948ce205298443c814d8c26faa9303492e019cef528da0940eba5616c3db3f`.
The exact six-field result has 342 distinct ordered rows over 48 explicitly
frozen identities: 192 owner, 80 candidate writer, 64 posting writer, six
stock reader, zero other, and zero PUBLIC rows.

## V05 binding and cross-check

The closed six-field V05 result contains exactly, in SQL order:

1. `aios_material_inventory_posting_writer,public,material_receipts,created_by_actor_reference,SELECT,NO`
2. `aios_material_receipt_candidate_writer,public,material_receipts,created_by_actor_reference,INSERT,NO`
3. `aios_material_receipt_candidate_writer,public,material_receipts,created_by_actor_reference,SELECT,NO`

Each tuple occurs exactly once in the R04 expected sequence. Candidate INSERT
is present; candidate UPDATE, posting UPDATE, and reader write are absent.
The SELECT rows may represent table privileges per column and are not claimed
to prove direct-column-ACL provenance.

## Privilege and N01 semantics

The validator keeps owner-derived privileges, table privileges represented per
column, direct column ACLs, membership, PUBLIC, effective rights, and
`is_grantable` distinct. N01 is unchanged and returns only bounded aggregate
counts: total receipts, NULL creator references, and invalid creator references.
NULL and invalid counts must both be zero; total may be zero or positive. It
returns no actor reference or business row.
