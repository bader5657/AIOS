# Stage 0.33B-V Authority Basis, Scope, and Historical Separation

Date: 2026-08-29 (Asia/Jakarta)

## Authority basis

Migration 0005 is **COMMITTED**. Its PR #249 one-shot migration authority is
**PERMANENTLY CONSUMED**; Migration 0005 rerun and `DOWN` are prohibited.
PR #251 exact-stream governance and PR #252 authority binding are merged and
verified. PR #253 was reviewed at
`13c1e11900715ad5856ba53f2804e5c1d1472e59` and merged as
`bf6cd4127765ef5052278fa6381ecae3c87b9ddd`.

Stage 0.33B-D historical semantic execution evidence remains **PERMANENTLY
INCOMPLETE**. Stage 0.33B-V cannot alter that classification. It establishes
only whether the current committed production state conforms to the reviewed
actor-provenance schema, privileges, preservation, security, and runtime
contract. It is not a Stage 0.33B-D replay, historical reconstruction, Migration
rerun, repair, or activation.

## Project Owner approval and activation boundary

The Project Owner approves one future bounded Stage 0.33B-V read-only
current-state verification session after this exact package receives independent
review, merges unchanged, and all pre-execution gates pass. Publication does not
activate the authority or execute Stage 0.33B-V.

The independent authority is single-use and authorizes exactly one PostgreSQL
session through one exact psql process. It is consumed at the first exact
production Docker/psql launch attempt regardless of outcome. Automatic retry,
an alternate connection, and a second psql process are prohibited. A later
verification requires fresh authority.

Approval includes no DDL, DML, `LOCK TABLE`, `GRANT`, `REVOKE`, `ALTER`,
`CREATE`, `DROP`, `TRUNCATE`, `COPY`, `SET ROLE`, mutating function,
advisory lock, sequence mutation, filesystem/program function,
`LISTEN`/`NOTIFY`, ownership repair, service/runtime change, Migration 0004
or 0005 execution, `DOWN`, or candidate activation.

## Exact session and transaction contract

The sole authorized control-plane argv is:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql -X -v ON_ERROR_STOP=1 --csv -t -q -P pager=off -U aios -d aios
```

The reviewed query bundle opens exactly:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL statement_timeout = '30s';
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
```

All observations derive from this single repeatable-read, read-only snapshot.
No table lock or `lock_timeout` is used. Success closes with `COMMIT;` only
after every bounded query. `ROLLBACK;` is permitted only to close the same
failed or incomplete read-only session.

## Frozen publication identities

- FRAME_NONCE:
  `0fba8f0c-4c0b-4101-9ed6-e1a597402394`.
- Exact bundle:
  `03_STAGE_0_33B_V_EXACT_QUERY_BUNDLE.sql`.
- Bundle SHA-256:
  `304fdf5fbf63bcea9c8e41ddb8e921831a9b4a01a1262acca2cfd09273e855f1`.
- Bundle bytes: `15808`.
- Framed chunks: `26` (`T00`, 25 semantic queries).
- Semantic queries: `25`.
- Order:
  `T00,I01,I02,S01,F01,F02,F03,F04,O01,O02,O03,O04,O05,O06,O07,O08,R01,R02,R03,R04,V01,V02,V03,V04,V05,N01`.

The executor submits these exact chunks incrementally, waits for durable
semantic evidence and its exact frame before advancing, and invents no SQL,
diagnostic query, replacement, reordering, omission, or `SELECT 1`.

## Evidence infrastructure prerequisite

The frozen namespace is
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v`.
It did not exist during publication. Its parent was root-owned, so separate
privileged, independently reviewed pre-execution provisioning is required.
Publication does not create or chmod/chown it. Provisioning must freeze safe
ownership, exclusive session-directory creation, and fail-if-exists behavior
before authority activation.

## Publication safety

This publication contacted no production PostgreSQL endpoint, launched no
production Docker/psql process, executed no production SELECT or migration,
created no production evidence session, and changed no production state.
Finalized Stage 0.33B-D evidence, `runtime.env`, services, Telegram, Universal
Ingestion, and candidate activation remain unchanged.
