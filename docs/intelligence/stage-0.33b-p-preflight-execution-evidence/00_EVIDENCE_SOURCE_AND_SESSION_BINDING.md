# Stage 0.33B-P Original Evidence Source and Session Binding

Date of recovery audit: 2026-08-28 (Asia/Jakarta)

## Classification and scope

This documentation-only package records a post-execution forensic binding to
an original retained Codex JSONL session. It does not contact production,
rerun Stage 0.33B-P, execute a migration, or authorize Stage 0.33B-A.

Evidence quality is **A. ORIGINAL EXECUTION EVIDENCE — SUFFICIENT**. The source
contains the original tool calls, exact Docker/psql argv, SQL write records,
process outputs, exit states, timestamps, ordering, post-session health record,
and final PASS classification. The final assistant report is corroborative and
is not used alone.

## Authoritative original source

| Property | Value |
|---|---|
| Absolute path | `/home/aiosadmin/.codex/sessions/2026/08/28/rollout-2026-08-28T18-16-40-01a04816-112d-7231-b987-fca86b496e91.jsonl` |
| Type | regular file / Codex JSONL rollout session |
| Size at audit | `9040633` bytes |
| mtime at audit | `2026-08-28 19:36:33.392436473 +0700` |
| inode at audit | `2885157` |
| Complete-file SHA-256 | `0d2ebc28adcdb8b4bab16ec65f9e1fd7627ef3cf5a93ba94d8d1a57fc4a16354` |
| Codex thread/session identity | `01a04816-112d-7231-b987-fca86b496e91` |
| Successful execution turn | `01a0485a-88ab-76b3-94ff-60f4857ce1bc` |
| Production command session | `56195` |
| Command launch timestamp | `2026-08-28T12:33:49.916Z` |
| First governed SQL write | `2026-08-28T12:34:01.063Z` |
| Command completion record | `2026-08-28T12:35:31.160Z` |
| Final PASS record | `2026-08-28T12:36:33.330Z` |

The complete original file was not copied into the repository and was not
modified. It may contain unrelated session material; only bounded safe record
identifiers and non-secret results are published here.

## Unambiguous authority and source correlation

The same original session records bind all of the following independent values:

- authorization PR `#247`, reviewed HEAD
  `4b6a753eed202ed5a3e70d4f2dd27c566b27b074`, and merge/current main
  `4a1ad5d0d2dee3c7c0d4837b375a9514e639d093`;
- canonical bundle SHA-256
  `64435ab0193ceb454569496f954a9c6788355f035834d7a6b095222b5154d6f3`;
- Migration 0005 UP SHA-256
  `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293`;
- target argv `/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql -X
  -v ON_ERROR_STOP=1 -U aios -d aios`; and
- the actual successful target, catalog, fingerprint, security, close, and
  health output recorded in the execution records.

PR #247 authority remains permanently consumed. Migration 0005 was not
executed and is not authorized by this package.

## Candidate-source disposition

`/home/aiosadmin/.codex/history.jsonl` and the later session
`rollout-2026-08-28T21-59-45-01a048e2-4d20-7361-9a3b-8caed5177f57.jsonl`
contain search-key matches but are not the authoritative execution source. The
two `/tmp/aios-stage-033bp-*.sql` files are canonical SQL inputs, not execution
output evidence. The authoritative source is the session identified above.

