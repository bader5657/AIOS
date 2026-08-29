# Stage 0.33B-V2A Exact Bundle, Semantic Contract, and Evidence Requirements

Date: 2026-08-29 (Asia/Jakarta)

## Exact V2 execution identity

The only authorized SQL input is the existing, non-duplicated bundle
`docs/intelligence/stage-0.33b-v2-bundle-and-frame-governance/03_STAGE_0_33B_V2_EXACT_QUERY_BUNDLE.sql`,
exactly 15,808 bytes with SHA-256
`afa22667313f2b199af78995b67b16257993cab8c124efb27f071238c32cf712`.
Its immutable publication-frozen frame nonce is the canonical lowercase UUIDv4
`b72accda-c7dc-49ba-bafb-6f0680d55910`; runtime replacement is forbidden.

The bundle has 25 semantic queries and 26 frames/chunks. PR #258 mechanically
proved that all 25 semantic SQL bodies are byte-identical to reviewed Stage V
bodies and that the only executable differences are 26 frame-nonce literals.
The query order is
`I01,I02,S01,F01,F02,F03,F04,O01,O02,O03,O04,O05,O06,O07,O08,R01,R02,R03,R04,V01,V02,V03,V04,V05,N01`.
PR #257 established PostgreSQL 17.10 semantic PASS 25/25 and frame PASS 26/26;
PR #258 validated transfer by exact semantic-body byte equivalence.

The future control-plane argv is exactly one process and one PostgreSQL session:

```text
/usr/bin/docker exec -i aios-postgres \
  /usr/local/bin/psql \
  -X \
  -v ON_ERROR_STOP=1 \
  --csv \
  -t \
  -q \
  -P pager=off \
  -U aios \
  -d aios
```

No alternative connection or second session is authorized. The exact bundle
transaction remains `BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ
ONLY;`, the reviewed canonical `SET LOCAL` statements, and `COMMIT`. DDL, DML,
LOCK TABLE, GRANT, REVOKE, ALTER, CREATE, DROP, TRUNCATE, COPY, SET ROLE,
LISTEN, NOTIFY, advisory locks, sequence mutation, and mutating functions are
forbidden.

## Corrected semantic contracts

R03 is a closed five-field 36-row contract: 28 owner-derived `aios` rows with
`is_grantable=YES` and eight governed non-owner `SELECT/NO` rows. Wildcard
normalization is forbidden.

R04 binds the self-contained manifest
`docs/intelligence/stage-0.33b-v2-r04-v05-semantic-correction/03_R04_EXACT_342_TUPLE_MANIFEST.json`,
raw SHA-256 `4f10acdff3da6e127f221356ebed7df0415668aad63d92ab04c79ab1ed92b183`
and canonical derived tuple SHA-256
`d7948ce205298443c814d8c26faa9303492e019cef528da0940eba5616c3db3f`.
It requires exactly 342 six-field rows: 192 owner, 80 candidate writer, 64
posting writer, six stock reader, zero other, and zero PUBLIC.

V05 requires exactly these six-field tuples once each:

1. `aios_material_inventory_posting_writer,public,material_receipts,created_by_actor_reference,SELECT,NO`
2. `aios_material_receipt_candidate_writer,public,material_receipts,created_by_actor_reference,INSERT,NO`
3. `aios_material_receipt_candidate_writer,public,material_receipts,created_by_actor_reference,SELECT,NO`

Candidate creator INSERT is present; candidate creator UPDATE, posting creator
UPDATE, and reader creator write are absent. The SELECT rows are not treated as
direct-column-ACL-only evidence.

F01-F04 are current-state observations and must not be compared with a
migration-time zero state. They emit no raw business rows. N01 emits only total
receipt count, NULL creator-reference count, and invalid creator-reference
count. PASS requires both defect counts to be zero; total may be zero or
positive. No raw creator reference is emitted.

## Durable semantic evidence

The verified persistent root is
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v`.
It must be a real non-symlink directory owned by `aiosadmin:aiosadmin` with mode
`0750`; no sudo provisioning is authorized. The future session exclusively
creates a unique child named
`stage-0.33b-v2-current-state-<UTC_TIMESTAMP>-<canonical-lowercase-UUIDv4>`.
No prior Stage V directory may be reused or modified.

The new child must contain `execution.jsonl`, `semantic-results.jsonl`, and
`manifest.json`. For every one of the 25 queries, retained evidence must contain
the actual bounded parsed payload or exact reviewed canonical representation,
plus session ID, query ID, frame ID, ordinal/order, timestamp, field count,
record count, semantic assertion, and PASS/FAIL. PASS-, frame-, or process-only
evidence is insufficient.

For every query the mandatory sequence is `receive frame -> parse result ->
validate result -> write semantic evidence -> flush/fsync -> advance`. All 25
pre-COMMIT semantic records must be durably complete before COMMIT.
