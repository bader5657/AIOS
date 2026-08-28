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

1. template SHA `53847f0bfb9b5e6595b25f83035726a2f10f0c3568baca2b863bea8f2961c693`;
2. Migration UP SHA `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`;
3. assembled SHA `bb11d884e9238fadb7537e32c18eb24df2e6ab1978b35e11af31dbbc2157c530`;
4. the single-marker raw-byte assembly method;
5. the 57-statement frozen order; and
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
