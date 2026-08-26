# AIOS Intelligence Writer Bootstrap Production Post-Execution Verification

Date: 2026-08-26 (Asia/Jakarta)

## Source and authority

The independent verification began with a clean worktree at
`a8a37de1ab87918fbeef3f4caef17a119482e24c`; `HEAD`, local `main`, and
`origin/main` were identical. The reviewed helper remains at
`scripts/admin/bootstrap_material_writer_secrets.py`. Its mechanically
recalculated SHA-256 was
`34aa8ec5c84606cfa559106bf3d32dc09f45aa98792393e746088e3a64cd5aa0`, exactly
matching the merged one-shot reauthorization authority in PR #225.

The Project Owner reported exactly one manual invocation and the sole emitted
line: `Writer bootstrap completed successfully; no secret values were emitted.`
The old failed authority and the successful replacement authority are both
`CONSUMED`. A helper rerun is `NOT AUTHORIZED`.

## Filesystem and secret structure

The observed production metadata was exact:

| Path | Owner:group | Mode | Type | Links |
|---|---|---:|---|---:|
| `/opt/aios` | `root:aiosadmin` | `0755` | directory | 16 |
| `/opt/aios/runtime` | `root:aiosadmin` | `0755` | directory | 10 |
| `/opt/aios/runtime/config` | `root:aiosadmin` | `0750` | directory | 2 |
| `/opt/aios/runtime/config/runtime.env` | `root:aiosadmin` | `0640` | regular file | 1 |

The new whole-file artifact SHA-256 is
`90f3813e1e33cb7a084f87e131d8315242400ae892c85c9f95659e63dc0eec98`.
Each governed key occurs exactly once and there is no duplicate governed key.
No value or value hash was displayed or recorded.

The retained sanitized execution evidence does not include a pre-bootstrap
copy or a digest of the environment with only the two governed assignments
removed. Therefore independent byte-for-byte comparison of unrelated entries
is unavailable. Preservation is supported by the reviewed helper's exact
unrelated-byte preservation and installed-file verification contract and its
successful completion, but this is the explicit verification limit; no secret
value was inspected or reproduced to close it artificially.

## PostgreSQL, identities, and isolation

Production `aios-postgres` was running and healthy on image
`postgres:17-alpine`, restart count `0`, serving database `aios` as PostgreSQL
17.10. Exactly the following four governed identities exist, with no additional
identity under either governed name prefix:

- `aios_material_receipt_candidate_writer`: NOLOGIN;
- `aios_material_receipt_candidate_runtime`: LOGIN, INHERIT;
- `aios_material_inventory_posting_writer`: NOLOGIN;
- `aios_material_inventory_posting_runtime`: LOGIN, INHERIT.

All four are NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, and
NOBYPASSRLS. Membership is exactly candidate runtime to candidate writer and
posting runtime to posting writer, with no cross, reader, third-role, or ADMIN
OPTION membership. Each identity owns zero databases, schemas, relations,
sequences, and routines; the complete ownership dependency check also passed.

The merged helper's exact read-only validation SQL passed independently against
the committed catalog. This proves the frozen candidate and posting database,
schema, table, column, unrelated-relation, direct/inherited privilege, grant
option, schema CREATE, and PUBLIC table/column ACL matrices. Candidate has only
the approved receipt/item candidate writes and stock reads and has no movement
or stock-write capability. Posting has only status/timestamp receipt/item
updates, approved movement inserts, and stock quantity/timestamp updates. All
enumerated immutable and business-content columns remain denied.

`aios_material_stock_reader` remains LOGIN, NOINHERIT, non-superuser,
non-CREATEDB, non-CREATEROLE, non-replication, non-BYPASSRLS, without membership
or ownership. Its effective access remains CONNECT to `aios`, USAGE of `public`,
and SELECT-only on `public.material_stock`, with no schema CREATE or governed
write privilege.

## Transport, authentication, and preservation

Administrative verification used only the fixed Docker plane:
`docker exec -i aios-postgres` to `/var/run/postgresql:5432`, role/database
`aios`. Runtime probes used only numeric loopback `127.0.0.1:5432`, database
`aios`, `sslmode=disable`, and the respective stored runtime credential. Docker's
effective and configured publication both resolve exactly to
`127.0.0.1:5432`; the container gateway is `172.16.2.1`. The applicable HBA rule
for that gateway is `scram-sha-256`, and `password_encryption` is
`scram-sha-256`.

Both runtime identities independently authenticated and returned exactly one
row from `SELECT 1`. No business query or mutation was attempted. There was no
admin/runtime transport crossover.

Production counts remained:

- `material_receipts`: `0`;
- `material_receipt_items`: `0`;
- `inventory_movements`: `0`;
- `material_stock`: `0`.

The bounded deterministic fingerprint of the empty `material_stock` content is
`d41d8cd98f00b204e9800998ecf8427e`. Because the recorded pre-bootstrap baseline
was also exactly zero rows, content is unchanged. No stock operation occurred.

`aios.service` remained `active/running`, MainPID `15845`, NRestarts `0`. Writer
credential provisioning required no service restart.

## Exposure, closure, and exclusions

The supplied execution evidence contains no password, password-bearing URI, or
environment content. The helper's output contract, successful output, and the
governance evidence reviewed here contain no secret value. This verification
did not search for or disclose secrets.

Runtime service implementation, Telegram work, production data population,
inventory movement creation, stock posting, and inference remain unauthorized.
The final classification is:

`MATERIAL_RECEIPT_AND_POSTING_WRITER_BOUNDARIES_VERIFIED`

The next separately governed task is:

`Material Receipt Candidate + Posting Repository/Service Boundary Implementation`

That future task may consume the provisioned identities in application code,
but it may not populate production data or activate Telegram automatically.

`WRITER BOOTSTRAP PRODUCTION VERIFICATION PASS — CANDIDATE AND POSTING BOUNDARIES READY`
