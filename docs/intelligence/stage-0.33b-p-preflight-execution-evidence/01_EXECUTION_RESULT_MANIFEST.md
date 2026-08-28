# Stage 0.33B-P Execution Result Manifest

This manifest was derived after execution from the original retained Codex
session identified in `00_EVIDENCE_SOURCE_AND_SESSION_BINDING.md`. Every value
below is traceable to bounded original records; no missing value or timestamp
was reconstructed.

## Command, input, order, and result

- Original command launch: ordinal `983`, JSONL line `984`, timestamp
  `2026-08-28T12:33:49.916Z`.
- Launch result/session identity: ordinal `984`, line `985`, process session
  `56195`.
- Exact SQL writes: ordinals `990`, `997`, `1004`, `1011`, `1018`, `1025`, and
  `1034`; they retain P01-P05, I01-I02, M01-M02, S01, Z01, F01-F04, O01-O08,
  R01-R04, and C01 in that order.
- Corresponding output chunks: ordinals `991`, `998`, `1005`, `1012`, `1019`,
  `1026`, and `1035`.
- Process close: ordinal `1039`, line `1040`.
- Complete command result: ordinal `1040`, line `1041`, command execution ID
  `exec-27088f48-d769-4a8e-ac40-5ea1bec27a23`, status `completed`, exit code
  `0`, stdout `85502` bytes, stderr `0` bytes.
- Post-session health/result: ordinal `1048`, line `1049`, exit code `0`.
- Final PASS classification: ordinal `1055`, line `1056`.

The canonical source bundle was independently extracted and verified in the
same session as SHA-256
`64435ab0193ceb454569496f954a9c6788355f035834d7a6b095222b5154d6f3` with
the exact 28-label sequence. Mechanical concatenation of the seven retained
transport `chars` payloads is `10458` bytes and hashes to
`0e196fc188498bc6b74dc191b33f8b74bbfe96d1ae7f7280c72d93c7fb82dafa`.
It differs from the `10464`-byte canonical file only at the six write boundaries
where separator blank lines were not retransmitted. The original records retain
all 28 exact governed SQL statements in the authorized order; this package
records both identities and does not alter or normalize either source.

## Actual bounded production results

| Gate | Original execution result |
|---|---|
| Transaction | `BEGIN READ ONLY`; C01 `COMMIT` successful |
| Database / owner / user | `aios` / `aios` / `aios` |
| Schema / owner | `public` / `pg_database_owner` |
| Relation / kind / owner | `material_receipts` / `r` / `aios` |
| PostgreSQL | `17.10` |
| M01 creator column | absent (`0` rows) |
| M02 creator constraint | absent (`0` rows) |
| Stage 0.32 index | present, valid, ready, unique; one key `source_asset_reference`; approved active-source predicate excluding `REJECTED` and `CANCELLED` |
| `material_receipts` | `0` / `d41d8cd98f00b204e9800998ecf8427e` |
| `material_receipt_items` | `0` / `d41d8cd98f00b204e9800998ecf8427e` |
| `inventory_movements` | `0` / `d41d8cd98f00b204e9800998ecf8427e` |
| `material_stock` | `0` / `d41d8cd98f00b204e9800998ecf8427e` |
| O01 columns | `47` bounded rows |
| O02 constraints | `42` bounded rows |
| O03 indexes | `12` bounded rows |
| O04 owners/ACL | four governed tables owned by `aios`; ACL snapshot captured |
| O05-O06 triggers/functions | no non-internal governed-table triggers or associated functions |
| O07-O08 relations/schema/extensions | captured; `public` owner `pg_database_owner`; `plpgsql` 1.0 in `pg_catalog` |
| R01 roles | six frozen roles captured |
| R02 memberships | two governed runtime-to-writer memberships; ADMIN OPTION false for both |
| R03 table privileges | `36` bounded rows |
| R04 column privileges | `335` bounded rows |

The complete command record retains stdout and explicit empty stderr, status
`completed`, and exit code `0`. The post-session record retains the same
container identity, running/healthy status, restart count `0`, unchanged
`aios.service` identity including PID `1475877`, and unchanged `runtime.env`
metadata. The execution emitted no business rows and performed no DDL, DML,
lock, ownership, role, grant, runtime, integration, or activation mutation.
Migration 0005 and Migration 0004 were not executed.

## Classification

```text
STAGE 0.33B-P FRESH FULL READ-ONLY PRODUCTION PREFLIGHT PASS
— CORRECTED PRODUCTION TARGET IDENTITY VERIFIED
— ZERO EXISTING MATERIAL RECEIPTS
— FULL PRESERVATION BASELINE CAPTURED
— ELIGIBLE TO REQUEST STAGE 0.33B-A ONE-SHOT MIGRATION 0005 AUTHORIZATION
```

This evidence binding does not publish Stage 0.33B-A and does not authorize
Migration 0005 execution.

