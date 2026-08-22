# Package Control and Decision

## Decision baseline

| Item | Approved state |
|---|---|
| Stage 0.6.3 | `ISOLATED STAGING INSTALLATION VERIFIED — ACCEPTED — CLOSED` |
| Stage 0.6.4 warm benchmark | `VERIFIED — READY FOR SPECIAL-TEST GOVERNANCE` |
| Runtime | Ollama `0.32.13` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Official reliability | `20/21` (`95.24%`) |
| Warm validity | `20/20` |
| Warm latency | p50 `2021 ms`; p95 `2214 ms`; maximum `7152 ms` |
| Warm latency gate | `PASS`, p95 at most `30000 ms` |
| Production safety | `PASS` |
| Maximum final classification | `PASS_WITH_LIMITATION` |

The original cold request remains one permanently counted contained invalid
result. It is not repaired or replaced. Therefore `PASS_FOR_DEVELOPMENT` is
unreachable and the maximum final Stage 0.6.4 classification is
`PASS_WITH_LIMITATION`.

## Exact governance decision

This package authorizes exactly three remaining benchmark tests, and no other
inference:

1. one synthetic timeout test;
2. one controlled synthetic malformed-output containment test; and
3. one unload/recovery observation after the inference-related tests.

This is governance-only work. No test, inference, unload intervention,
production change, adapter implementation, or Brain integration is executed
by creation, review, publication, or activation of this package.
