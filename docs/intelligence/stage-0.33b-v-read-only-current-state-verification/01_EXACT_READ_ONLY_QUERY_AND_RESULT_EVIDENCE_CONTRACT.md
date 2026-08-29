# Stage 0.33B-V Exact Read-Only Query and Result-Evidence Contract

Date: 2026-08-29 (Asia/Jakarta)

## Exact bundle and reuse

The only executable SQL is
`03_STAGE_0_33B_V_EXACT_QUERY_BUNDLE.sql`, SHA-256
`304fdf5fbf63bcea9c8e41ddb8e921831a9b4a01a1262acca2cfd09273e855f1`.
Its 24 reused semantic statement bodies are byte-identical to PR #251:
`I01,I02,S01,F01-F04,O01-O08,R01-R04,V01-V05`. Only `N01` is new.
Transaction controls and all frames are Stage 0.33B-V-specific.

The parser is Python standard-library
`csv.reader(stream, delimiter=',', quotechar='"', doublequote=True,
strict=True)` over raw UTF-8 with `newline=''`. stdout is CSV results only;
stderr is a separate bounded diagnostic channel and is never parsed as data.

Every exact frame is
`["AIOS_FRAME", QUERY_ID, "0fba8f0c-4c0b-4101-9ed6-e1a597402394"]`.
Wrong/missing/duplicate/out-of-order frames, malformed CSV, unexpected records,
field-width mismatch, cardinality mismatch, or semantic mismatch fail closed.
Frame or process PASS without retained semantic payload is insufficient.

## Result manifest and assertions

| ID | Width/cardinality | Current-state assertion |
|---|---|---|
| I01 | 4 / exactly 1 | database/session/schema are `aios/aios/public`; PostgreSQL major is 17 |
| I02 | 7 / exactly 1 | `aios/aios/public/pg_database_owner/material_receipts/r/aios` |
| S01 | 7 / exactly 1 | named Stage 0.32 index is valid, ready, unique, one-key `source_asset_reference`, with the exact reviewed active-source predicate |
| F01-F04 | 2 / exactly 1 each | observed current row count and canonical digest retained; no zero-count expectation |
| O01 | 6 / ordered list | exact four-table columns/types/nullability/defaults snapshot; all four governed relations represented |
| O02 | 4 / ordered list | exact four-table constraint snapshot |
| O03 | 7 / ordered list | exact four-table index snapshot; unexplained index drift fails |
| O04 | 3 / exactly 4 | four governed table owners/ACLs; owners remain `aios` |
| O05 | 3 / ordered list | exact non-internal trigger snapshot; unexplained trigger fails |
| O06 | 5 / ordered list | exact functions referenced by O05; definitions retained, functions never executed |
| O07 | 3 / exactly 1 | `public` owner is `pg_database_owner`; ACL snapshot retained |
| O08 | 3 / ordered list | bounded extension snapshot retained |
| R01 | 8 / exactly 6 | exact governed role attributes only |
| R02 | 3 / ordered list | exact governed memberships and ADMIN OPTION; candidate runtime→writer and posting runtime→writer remain governed |
| R03 | 5 / ordered list | exact governed four-table privilege snapshot |
| R04 | 6 / ordered list | exact governed four-table column-privilege snapshot |
| V01 | 4 / exactly 1 | creator column is `created_by_actor_reference/text/true/no default` |
| V02 | 3 / exactly 1 | exact named CHECK, type `c`, exact canonical lowercase operator UUIDv4 grammar |
| V03 | 2 / exactly 0 | no index definition references creator provenance |
| V04 | 7 / exactly 1 | same exact Stage 0.32 index assertion as S01 |
| V05 | 6 / exactly 1 | only candidate writer creator-column `INSERT/NO` appears among the four frozen non-owner roles |
| N01 | 3 / exactly 1 | observed total count; null creator count `0`; invalid-format count `0` |

O/R list results are complete ordered tuples, not wildcard discovery. Their
validator applies the reviewed PR #251 exact field, multiplicity, role-set,
ownership, privilege, membership, ACL, object, and definition rules. The
candidate writer has only the approved creator-column INSERT grant, no creator
UPDATE; posting roles gain no creator UPDATE; reader roles gain no write
authority. Any unexplained schema/security tuple fails. Current business counts
and digests may differ from migration time and are classified only as
`OBSERVED_CURRENT_STATE`.

N01 emits aggregates only and never an actor reference. It cannot establish
Stage 0.33B-D Z01 or when any current row was created. The CHECK is verified
through catalog definition plus aggregate integrity; synthetic INSERT is
prohibited.

## Durable semantic evidence before advance

For every semantic ID the executor writes an exclusive
`semantic-results.jsonl` record binding session ID, query ID, frame ID/order,
UTC timestamp, field count, record count, validator contract/version, exact
semantic assertion, PASS/FAIL, and either the actual bounded parsed tuple list or
an explicitly reviewed canonical representation and SHA-256 sufficient for
independent verification. This catalog/scalar bundle should retain exact parsed
tuples. F01-F04 and N01 retain only bounded aggregates.

The record and containing directory are flushed/fsynced before the next chunk.
All pre-COMMIT semantic evidence must be durable before `COMMIT`. Failure to
retain it sends only `ROLLBACK;` through the same live read-only session where
possible, consumes authority, and cannot claim complete verification.

## Privacy and final evidence

Raw business rows, actor UUIDs/references, receipt/material/stock/movement,
supplier, Telegram, or document content are prohibited. Passwords, tokens, API
or private keys, `DATABASE_URL`, credential-bearing DSNs, `runtime.env`
contents, environment dumps, and unbounded tracebacks are prohibited.

The exact evidence set is `execution.jsonl`, `semantic-results.jsonl`, and
`manifest.json`. It requires exclusive creation, bounded stderr, secret scan,
file and directory flush/fsync, immutable final mode, SHA-256, byte size, and
record count. The manifest binds bundle SHA, nonce, argv, parser, validator
version, session identity, transaction outcome, and all evidence identities.
Evidence must be independently reviewable without reconnecting to production.

## Disposable validation result

Publication validation passed against an isolated `postgres:17-alpine`
container using tmpfs storage, `--network none`, no host port, and a direct
non-production schema fixture. No Migration 0005 or other migration artifact
was executed. The exact bundle completed with empty stderr; strict
`csv.reader` parsing received all 26 frames once in order, attributed all 25
semantic payloads, passed the frozen widths/cardinalities and fixture semantic
assertions, and durably fsynced 25 semantic-result records under `/tmp`.

N01 returned `0/0/0`; no canonical actor-reference value and no raw business
row was emitted. Validation stdout SHA-256 was
`0769d384434c33bec8c2e483ea034045891d75b19eed1201cf4a8115964488e8`;
the disposable semantic-results SHA-256 was
`47d66597425c8dd006369a8808d837b55fafcc4995cef51de5291f4d6c581214`.
A negative disposable probe received `cannot execute CREATE TABLE in a
read-only transaction`, confirming mutation rejection.

Before activation, the exact bundle and production executor must still pass
pre-launch identity checks. Disposable observations are validation evidence
only, never production observations.
