# Stage 0.33B-DS Authority Dependency and Stream Scope

Date: 2026-08-29 (Asia/Jakarta)

## Publication boundary

This package is governance and execution-contract documentation only. It does
not contact production PostgreSQL, launch Docker/`psql`, execute a production
`SELECT`, create an execution-evidence session, run Migration 0005 or 0004,
alter the provisioned evidence root or `runtime.env`, restart a service, change
Telegram or Universal Ingestion, or activate candidate traffic.

Stage 0.33B-A PR `#249` is merged at
`48a8c24d06e75de0c1ff8aa708db7a386b4fb7c4`; its reviewed head is
`9358efcf820f272689ff9a6c267da8956025a69d`. Stage 0.33B-FP PR `#250`
provisioning is PASS. The earlier Stage 0.33B-D activation stopped before
evidence-session creation and before the first production control-plane launch,
so the one-shot authority remains ACTIVE / UNCONSUMED.

## Supplemental scope

`01_STAGE_0_33B_D_EXACT_SQL_STREAM.sql` is the sole authoritative success-path
SQL template. It supplements but does not replace, expand, or consume PR #249.
It freezes transaction controls, four locks, every pre-DDL verifier, one unique
Migration 0005 insertion marker, every post-UP verifier, repeated preservation
queries, and the sole success-path `COMMIT`.

The I01-I02, M01-M02, S01, Z01, F01-F04, O01-O08, and R01-R04 statement bodies
are reused from the previously reviewed canonical Stage 0.33B-P bundle. V01-V05
are new because the prior bundle observed only the pre-Migration state. PF01-PF04
reuse F01-F04 exactly. PO01-PO08 and PR01-PR04 reuse O01-O08 and R01-R04 exactly.

Their authoritative source is the `CANONICAL EXECUTABLE PREFLIGHT SQL BUNDLE`
in `docs/intelligence/stage-0.33b-read-only-production-preflight-authorization/01_READ_ONLY_QUERY_AND_EVIDENCE_CONTRACT.md`,
whose reviewed canonical bundle identity is
`64435ab0193ceb454569496f954a9c6788355f035834d7a6b095222b5154d6f3`.
Mechanical comparison passed for all 22 reused prior statement bodies and all
16 repeated post-DDL statement bodies.

The executor must run the assembled stream incrementally through the single
governed `psql` process and validate each bounded result before sending the next
section. On a mismatch before `COMMIT`, it sends only `ROLLBACK;` through that
same existing session and does not send the remaining success stream. It must
never open another connection. The complete assembled hash identifies the
approved PASS path; a fail-closed prefix plus `ROLLBACK;` is retained as bounded
failure evidence.

## Mechanical gate expectations

- I01-I02 must equal the frozen target tuple in PR #249 and PostgreSQL major 17.
- M01-M02 must return zero rows.
- S01 must return exactly one valid, ready, unique, one-key approved index row.
- Z01 must return `0`.
- F01-F04 must each return `0 / d41d8cd98f00b204e9800998ecf8427e`.
- O01-O08 and R01-R04 are retained as the deterministic pre-DDL baseline.
- V01-V05 must prove the exact three-part Migration 0005 delta.
- PF01-PF04 must byte-match their pre-DDL results.
- PO/PR outputs must equal their pre-DDL counterparts after removing only the
  V01 creator-column row, V02 creator-CHECK row, the exact candidate-writer
  creator-column `INSERT` privilege row, and the four owner-derived `aios`
  creator-column privilege rows (`INSERT`, `REFERENCES`, `SELECT`, `UPDATE`)
  that information_schema represents for every owner-owned column. Those four
  rows are a deterministic representation of the new column and are not an ACL
  grant delta.
- Every other row and field must compare byte-for-byte after the same UTF-8,
  line, field, NULL, and ordering treatment used for both sides.

No runtime SQL generation, query invention, diagnostics, equivalent-expression
substitution, reordering, omission, addition, or `psql` meta-command is allowed.

## Binding decision

Supplemental governance alone does not silently amend already-merged PR #249.
After this package receives independent review PASS and merges unchanged, a
narrow follow-up Stage 0.33B-A authority-binding amendment is required to bind
the still-unconsumed authority to the reviewed template SHA, Migration UP SHA,
assembled-stream SHA, unique-marker assembly method, and incremental same-session
gate procedure. Production execution remains blocked until that amendment is
independently reviewed and merged.

## PR #251 remediation: exact result framing

FRAME_NONCE is permanently frozen as `a3e1a015-c078-44b4-a618-f6c7f49831f7` (canonical lowercase UUIDv4; never runtime-generated). Exact argv: `/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql -X -v ON_ERROR_STOP=1 --csv -t -q -P pager=off -U aios -d aios`. stdout is CSV only; stderr is separate bounded diagnostics and never parsed. Python `csv.reader` parses raw UTF-8 with `newline=''`, delimiter `,`, quotechar `"`, `doublequote=True`, strict malformed-record failure.

Frames are exact three-field records `["AIOS_FRAME", SECTION_ID, FRAME_NONCE]`. The 49 unique frames occur once in frozen order: `T01-T07,L01,L02,L03,L04,I01,I02,M01,M02,S01,Z01,F01,F02,F03,F04,O01,O02,O03,O04,O05,O06,O07,O08,R01,R02,R03,R04,X01,V01,V02,V03,V04,V05,PF01,PF02,PF03,PF04,PO01,PO02,PO03,PO04,PO05,PO06,PO07,PO08,PR01,PR02,PR03,PR04`. Missing, duplicate, unexpected, out-of-order, wrong-nonce, malformed, or unattributed records fail.

Production sends 49 incremental chunks (T01-T07 is one prefix chunk), waiting for each frame and semantic gate before the next; bulk send is forbidden. Zero data records plus a matching frame proves an executed zero-row result; no frame does not. COMMIT is final SQL. Semantic mismatch sends exactly `ROLLBACK;` in the same live session; ON_ERROR_STOP termination permits no retry or second connection.

## Exact field-level comparison manifest

Results are ordered lists of complete CSV tuples. Exact unchanged pairs: `O03=PO03,O04=PO04,O05=PO05,O06=PO06,O07=PO07,O08=PO08,R01=PR01,R02=PR02,R03=PR03,F01=PF01,F02=PF02,F03=PF03,F04=PF04`.

Frozen disposable PostgreSQL 17 tuples: PO01 `["material_receipts","14","created_by_actor_reference","text","t",""]`; PO02 `["material_receipts","material_receipts_created_by_actor_reference_valid","c","CHECK ((created_by_actor_reference ~ '^operator:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'::text))"]`; PR04 candidate `["aios_material_receipt_candidate_writer","public","material_receipts","created_by_actor_reference","INSERT","NO"]`; owner rows are the four `["aios","public","material_receipts","created_by_actor_reference", PRIV, "NO"]` tuples for PRIV=`INSERT`,`REFERENCES`,`SELECT`,`UPDATE`.

PO01/PO02 require empty pre-only, exactly one post-only full-tuple match, remove one occurrence, then exact ordered equality. R04 requires empty pre-only and exactly the five frozen tuples (multiplicity one), remove them, then exact ordered equality. V01/V02/V05 cross-check the deltas. No wildcard or substring filtering.

Updated identities: template SHA `bc9860db9bebb8be5dea5bea2c316d2e99cd3e5e1dccda6d6fd4adc3cbb42fb3`; assembled SHA `ce89b4c357e7b0bb52316b363163d8342afbf9cb1e3eaafb98fad8fca5a49799`; 26558 bytes; 57 semantic, 49 framing, 106 physical statements; 49 chunks. PR #249 remains ACTIVE / UNCONSUMED and requires a later explicit argv/protocol binding amendment.

### Frozen statement/result attribution

Every result is accepted only after its exact preceding frame and statement ID. The manifest is: I01(4,1), I02(7,1), M01/M02(1,0), S01(7,1), Z01(1,1), F01-F04(2,1 each), O01(6,list), O02(4,list), O03(7,list), O04(3,list), O05(3,list), O06(5,list), O07(3,list), O08(3,list), R01(8,list), R02(3,list), R03(5,list), R04(6,list), V01(6,1), V02(4,1), V03(1,0), V04(7,1), V05(3,1), PF01-PF04(2,1 each), PO01(6,list), PO02(4,list), PO03-PO08(equal O03-O08), PR01-PR03(equal R01-R03), PR04(6,list). Cardinality and semantic rules are frozen by the corresponding gate and exact tuple comparison above.
