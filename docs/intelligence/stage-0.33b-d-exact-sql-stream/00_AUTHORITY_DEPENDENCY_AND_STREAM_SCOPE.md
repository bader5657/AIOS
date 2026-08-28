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
