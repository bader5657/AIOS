# Stage 0.33B-V2C Privilege Audit and Disposable Validation

Date: 2026-08-29 (Asia/Jakarta)

## Query semantics matrix

| Query | Proves | Does not prove |
|---|---|---|
| R01 | exact six role attributes | ACL source or effective object access |
| R02 | exact governed memberships and ADMIN OPTION | independent direct ACL source |
| R03 | closed table-privilege representation: 28 owner `YES`, 8 non-owner SELECT `NO` | column grants or raw ACL provenance |
| R04 | complete closed 342-row column-privilege representation | whether a represented privilege originated at table or column scope by itself |
| V05 | exact three-row non-owner creator-column security snapshot | direct-ACL provenance for its SELECT rows |

Owner-derived rights, direct ACLs, table privileges represented per column,
membership, PUBLIC, effective privilege, and `is_grantable` are treated as
distinct concepts. Rejected assumptions include owner `is_grantable=NO`,
`column_privileges` meaning direct column grants only, V05 returning one row,
and table SELECT not appearing at column level.

PR #256's R03 contract remains unchanged: exactly 36 rows, comprising 28 owner
`YES` tuples and eight governed non-owner SELECT/NO tuples.

## Disposable full semantic validation

A fresh `postgres:17-alpine` container used network mode `none`, tmpfs database
storage, no host port, no production credential, and a direct representative
post-0005 schema/role fixture. No production endpoint was contacted.

The unchanged Stage V query bundle executed as one repeatable-read, read-only
transaction. Strict CSV parsing observed all 26 frames in exact order and all
25 semantic payloads. Corrected closed R03, R04, and V05 validators passed;
all other existing semantic validators also passed. Result: PostgreSQL 17.10,
psql exit 0, stderr 0 bytes, semantic coverage 25/25.

The validation writer retained and fsynced one bounded actual-payload record per
semantic query. The disposable 25-record JSONL was 53803 bytes with SHA-256
`2a230ceba7e09bd44ffaa28d1611f30d9b971ee3636a9040b33442fbad5edcf9`,
then removed with the disposable environment. This demonstrates the hardened
semantic-retention model without retaining fixture output as production
evidence.

Negative contract checks require failure for missing, extra, duplicate, wrong
grantee/table/column/privilege/grantability rows, unexpected PUBLIC or runtime
rows, candidate/posting creator UPDATE, reader write, and any other unexpected
non-owner write.

Mechanical manifest tests derived exactly 342 distinct ordered tuples with
counts `192/80/64/6`. Exact comparison against the disposable R04 output passed
row-for-row. Mutations for a missing owner tuple, owner `YES` changed to `NO`,
extra candidate privilege, missing posting SELECT, reader write, PUBLIC row,
duplicate tuple, extra governed column, wrong order, wrong table, and wrong
grantee each failed exact equality. All three V05 tuples occur exactly once in
the derived R04 sequence.

R04 SQL changed: **NO**. V05 SQL changed: **NO**. All 25 future semantic SQL
bodies may remain byte-identical. This package grants zero production sessions,
creates no Stage V2 authority, and does not change the historical failed Stage
V result or consumed authority. Stage D historical semantic evidence remains
permanently incomplete. The actor-provenance gate remains open and candidate
activation remains not authorized.

