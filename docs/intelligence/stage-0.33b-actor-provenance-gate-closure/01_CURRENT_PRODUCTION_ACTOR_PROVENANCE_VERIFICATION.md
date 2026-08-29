# Stage 0.33B-VC Current Production Actor-Provenance Verification

Date: 2026-08-29 (Asia/Jakarta)

## Complete semantic evidence

Offline parsing found exactly one PASS record for every ordered semantic ID
`I01,I02,S01,F01,F02,F03,F04,O01,O02,O03,O04,O05,O06,O07,O08,R01,R02,R03,R04,V01,V02,V03,V04,V05,N01`.
Coverage is 25/25, with zero missing or duplicate query IDs and zero missing
bounded payloads. Every record binds query/frame ID, ordinal, UTC timestamp,
field and record counts, actual bounded parsed payload, payload hash, assertion,
and PASS. The exact 26-frame contract and frozen nonce are bound with no old
nonce or ordering ambiguity.

I01/I02 prove database and session user `aios`, database owner `aios`, schema
`public`, schema owner `pg_database_owner`, PostgreSQL major 17, and
`material_receipts` as relkind `r` owned by `aios`.

S01 and V04 contain the identical reviewed
`material_receipts_source_asset_active_uidx` tuple: present, valid, ready,
unique, one key `source_asset_reference`, and the exact active predicate
excluding `REJECTED` and `CANCELLED` states. F01-F04 are current observations:
all four governed tables contain zero rows with the canonical empty digest.
They do not reconstruct Stage D history.

O01-O08 and R01/R02 all PASS with retained bounded structural, security, role,
membership, ownership, ACL, trigger/function-definition, schema, and extension
payloads. No unresolved object, ADMIN OPTION, membership, or security drift
remains.

## Corrected privilege and provenance contracts

R03 exactly equals the corrected closed 36-row, five-field sequence: 28
owner-derived `aios` rows with `is_grantable=YES`, eight governed non-owner
`SELECT/NO` rows, and no extra, duplicate, PUBLIC, or unexpected non-owner
write row.

R04 exactly equals the PR #257 self-contained ordered 342-row contract. The
manifest SHA-256 is
`4f10acdff3da6e127f221356ebed7df0415668aad63d92ab04c79ab1ed92b183`
and canonical tuple SHA-256 is
`d7948ce205298443c814d8c26faa9303492e019cef528da0940eba5616c3db3f`.
Counts are 192 owner, 80 candidate writer, 64 posting writer, six stock reader,
zero other, and zero PUBLIC.

V01 proves `created_by_actor_reference` is text, NOT NULL, and has no default.
V02 proves the exact named creator CHECK with canonical lowercase
`operator:<UUIDv4>` semantics. V03 returns zero unexpected provenance indexes.
V05 contains exactly posting SELECT/NO, candidate INSERT/NO, and candidate
SELECT/NO on the creator column. Candidate INSERT is present; candidate UPDATE,
posting UPDATE, and reader write are absent.

N01 is exactly `total=0, null=0, invalid=0`. Evidence contains no raw actor
reference and no raw business row. The bounded secret scan PASS found no
password, token, API key, private key, `DATABASE_URL`, credential-bearing DSN,
or `runtime.env` contents.

Runtime identity is preserved: the container remained running/healthy with
restart count zero and unchanged identity/start time; `aios.service` remained
active/running with unchanged PID/start identity; `runtime.env` metadata,
Telegram, and Universal Ingestion remained unchanged; candidate activation
remained `NO`. DDL, DML, GRANT/REVOKE, ownership/runtime mutation, and migration
execution during V2 were all absent.

Therefore Migration 0005 **CURRENT PRODUCTION STATE IS VERIFIED**. This is a
current-state conclusion, never a reconstruction of historical execution.
