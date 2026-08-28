# Stage 0.33B-DS Disposable PostgreSQL Validation and Execution Binding

## Isolated validation boundary

Validation used a disposable `postgres:17-alpine` container with networking
disabled, synthetic governed roles, a synthetic database `aios` owned by
synthetic role `aios`, and empty schemas created from committed Migrations
0002-0004. It used no production network, container, endpoint, credential,
secret, configuration, or data. PostgreSQL reported `17.10`.

The exact in-memory assembled success stream identified in `02_...md` was sent
to that isolated database with `ON_ERROR_STOP=1`. Validation completed with exit
code zero and C01 `COMMIT`.

## Validated results

- I01-I02 returned database/owner/user `aios`/`aios`/`aios`, schema/owner
  `public`/`pg_database_owner`, relation/kind/owner
  `material_receipts`/`r`/`aios`, and PostgreSQL `17.10`.
- M01-M02 returned zero rows.
- S01 returned one valid, ready, unique, one-key `source_asset_reference` index
  with the approved predicate excluding `REJECTED` and `CANCELLED`.
- Z01 returned zero.
- F01-F04 and PF01-PF04 each returned
  `0 / d41d8cd98f00b204e9800998ecf8427e`.
- O/R and PO/PR statements executed deterministically.
- The exact Migration 0005 UP bytes executed inside the same transaction.
- V01 returned one `text`, NOT NULL, no-default creator column.
- V02 returned one named CHECK whose rendered definition preserves lowercase
  hex, canonical hyphens, version nibble `4`, and RFC 4122 variant `[89ab]`.
- V03 returned zero creator-provenance indexes.
- V04 returned the unchanged Stage 0.32 index.
- V05 returned exactly one non-owner row:
  `aios_material_receipt_candidate_writer | INSERT | NO`.
- Post-DDL O01 added only the creator-column row; O02 added only the named CHECK;
  R04 added the candidate-writer creator-column INSERT row plus the four
  deterministic owner-derived `aios` privilege rows (`INSERT`, `REFERENCES`,
  `SELECT`, `UPDATE`) that information_schema emits for the new owner-owned
  column. Those owner-derived rows are not ACL mutations. Other governed
  synthetic snapshot output was unchanged.
- The transaction committed and zero business rows existed before and after.

## Rollback-path validation

A second isolated synthetic database was initialized at the same empty
prestate. The same assembled statements through all verifiers were executed,
but the validation harness substituted executor-side `ROLLBACK;` for the final
success `COMMIT;`. After rollback, independent disposable catalog checks found
creator column `0`, named creator CHECK `0`, and candidate-writer creator-column
INSERT privilege `0`. This proves transactional rollback of the exact three-part
delta without executing Migration 0005 DOWN.

## Grammar equivalence

The committed database CHECK and the governed application contract both require
`operator:<canonical-lowercase-UUIDv4>`: lowercase hexadecimal, canonical
8-4-4-4-12 hyphens, version nibble `4`, and variant nibble `[89ab]`. Validation
observed the exact committed CHECK definition; no weakening or alternate grammar
was introduced.

## Execution and authority binding

This publication does not activate its own execution authority and does not
consume PR #249. Production launch remains blocked after this PR until a narrow
follow-up authority amendment binds PR #249's still-unconsumed one-shot authority
to all of:

1. template SHA `bc9860db9bebb8be5dea5bea2c316d2e99cd3e5e1dccda6d6fd4adc3cbb42fb3`;
2. Migration UP SHA `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`;
3. assembled SHA `ce89b4c357e7b0bb52316b363163d8342afbf9cb1e3eaafb98fad8fca5a49799`;
4. the single-marker raw-byte assembly method;
5. the 106-statement physical SQL order; and
6. incremental result validation and same-session fail-closed rollback.

The future execution evidence must durably record those identities and assembly
facts before the first production control-plane launch. No production SQL may be
invented, added, removed, reordered, or substituted at runtime.

## Publication safety record

| Control | Result |
|---|---|
| Production PostgreSQL contacted / SELECT | `NO / NO` |
| Production control-plane launch / lock / DDL | `NO / NO / NO` |
| Migration 0005 production execution | `NOT EXECUTED` |
| PR #249 one-shot authority | `ACTIVE / UNCONSUMED` |
| Production evidence session | `NOT CREATED` |
| Provisioned evidence root | `UNCHANGED` |
| `runtime.env` / services | `UNCHANGED` |
| Telegram / Universal Ingestion | `UNCHANGED` |
| Candidate activation | `NO` |

```text
STAGE 0.33B-DS EXACT PRODUCTION SQL STREAM GOVERNANCE PUBLISHED
— COMPLETE EXECUTION STREAM MECHANICALLY RECOVERABLE
— EXACT TEMPLATE / MIGRATION / ASSEMBLED STREAM HASHES FROZEN
— DISPOSABLE POSTGRESQL VALIDATION COMPLETE
— PRODUCTION LAUNCH NOT ATTEMPTED
— PR #249 ONE-SHOT AUTHORITY REMAINS UNCONSUMED
— READY FOR INDEPENDENT EXACT-STREAM GOVERNANCE REVIEW
— MIGRATION 0005 NOT EXECUTED
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
```

## Remediation validation record

Disposable PostgreSQL 17.10 validation used the exact argv, raw UTF-8 stdout/stderr separation, and strict `csv.reader` contract. All 49 frames were received exactly once and in order; every result was attributed to its preceding statement ID, including multiline `pg_get_functiondef` CSV fields. M01/M02 produced zero records followed by their frames; Z01's scalar was attributed correctly; O/R and V multi-row results were attributed correctly. Missing/duplicate/out-of-order/wrong-nonce/wrong-section/unexpected-record, malformed CSV, and truncated quoted multiline harness inputs all failed.

The comparison harness records bounded counts and exact-match status for O01/PO01, O02/PO02, R04/PR04, and every unchanged pair. Synthetic adversarial records (wrong type, nullable/default/ordinal, altered CHECK or type, candidate grantability/privilege changes, extra/missing/duplicate owner rows, unexpected column/constraint, and any O/R field change) all failed exact tuple comparison.

Success used incremental chunks and committed with C01 final. Semantic-failure validation sent exactly `ROLLBACK;` on the same live psql session and observed no migration objects afterward. SQL-error validation under ON_ERROR_STOP terminated psql; no retry or second connection was launched, and rollback was treated as fail-closed through termination.

Evidence pre-launch requirements now include reviewed PR HEAD, exact argv, template/Migration/assembled hashes, byte size 26558, 57 semantic statements, 49 framing statements, 106 physical statements, 49 frames, 49 chunks, nonce, parser configuration, exact-delta manifest hash/version, framing PASS, and assembly PASS.
