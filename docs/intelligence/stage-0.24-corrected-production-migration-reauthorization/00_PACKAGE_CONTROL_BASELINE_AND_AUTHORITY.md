# AIOS Intelligence Stage 0.24 — Corrected Production Migration Reauthorization

| Control | Authorized value |
|---|---|
| Authority baseline | `9ea0dfc745d06564809dbbc8fdbf99f9e9265aac` |
| Failure-review governance commit | `83c0b014ac5efb47d19409c5ffe89d7b5844345c` |
| Failure-review merge commit | `9ea0dfc745d06564809dbbc8fdbf99f9e9265aac` |
| Previous failure | `NON_PERSISTENT_PRODUCTION_SCHEMA_VERIFICATION_QUERY_FAILURE` |
| Previous authority | `CONSUMED` |
| New authority | exactly one fresh controlled production attempt |
| Retry | `NONE` |
| Execution during publication | `PROHIBITED` |
| Maximum persistent result | one empty `material_stock` table |

PR #206 was reviewed as governance/documentation-only, then normally merged.
At the resulting baseline, `HEAD == main == origin/main`, the worktree was
clean, and both migration identities remained exact:

- up: `migrations/postgres/0002_create_material_stock.up.sql`, SHA-256
  `a6d4a7be98fe8ecb6914a6231f9d2ddcd76e2ec7fb30a87759d8ba6be9320d5f`;
- down: `migrations/postgres/0002_create_material_stock.down.sql`, SHA-256
  `045dc369c3b0a7174463bdb80a9b1831666f8827a857226da52a9ec670e9b0c3`.

Neither migration is modified or superseded. The first attempt is historical
evidence and does not count against the one new attempt. Its authority remains
consumed and may not be reused.

This package is reauthorization governance only. Publication performs no
database mutation or migration execution. The fresh authority activates only
after this package is merged into `main` and a future operator passes every
source and production preflight gate.
