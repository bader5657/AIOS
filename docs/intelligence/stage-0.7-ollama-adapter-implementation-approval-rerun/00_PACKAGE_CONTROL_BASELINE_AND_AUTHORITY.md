# AIOS Intelligence Stage 0.7 — Ollama Provider Adapter Implementation Approval Rerun

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / IMPLEMENTATION APPROVAL ONLY` |
| Approval baseline | `e6f8e308c4713ed697fb98934e95fcc15b685ce9` |
| Baseline state | `HEAD == main == origin/main`; tracked worktree clean |
| Stage 0.6.4 | `BENCHMARK PASS WITH LIMITATION — VERIFIED — ACCEPTED — CLOSED` |
| Adapter boundary | `IDENTIFIED` |
| Input payload contract | `VERIFIED — ACCEPTED — CLOSED` |
| Architecture change required | `NO` |
| Implementation disposition | `APPROVED — READY TO BUILD` |
| Live staging / Brain / production authority | `NONE` |

The closed two-key input payload contract resolves the sole blocker recorded by
the first implementation-approval evaluation. The existing Brain contracts,
provider abstraction, local runtime decision, adapter boundary, security/
privacy restrictions, and benchmark limitation remain controlling.

This package authorizes only the exact repository implementation and unit-test
scope below. It does not implement anything, execute inference, contact or
modify staging, connect Brain orchestration, modify Core, add dependencies, or
grant production authority.

## Preserved benchmark limitation

`The first official cold structured-output request produced a contained schema-invalid confidence value (100 instead of 0.0–1.0). The result was rejected correctly. After methodology clarification, all 20 official warm requests were valid. Official reliability is therefore 20/21 (95.24%).`

The adapter must preserve fail-closed rejection. It may not coerce `100` to
`1.0`, repair output, retry, or hide this limitation.
