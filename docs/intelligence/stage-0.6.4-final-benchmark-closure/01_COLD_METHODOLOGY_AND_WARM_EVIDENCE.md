# Cold Methodology and Warm Benchmark Evidence

## Original official cold request

| Field | Evidence |
|---|---|
| HTTP | `200` |
| Latency | `5953 ms` |
| Output | `{"category":"normal","confidence":100}` |
| Schema | `INVALID` |
| Classification | `CONTAINED_INVALID_RESULT` |

The confidence value `100` is outside the required `0.0–1.0` range. The result
was rejected before downstream acceptance. It remains permanently retained as
the first request in the official 21-request denominator and is not erased,
reclassified, repaired, or replaced.

## Methodology reconciliation and corrected cold evidence

The merged methodology reconciliation authorized one corrected cold rerun to
validate the clarified structured-output method. It did not authorize changing
the original evidence or reliability denominator.

| Field | Evidence |
|---|---|
| HTTP | `200` |
| Latency | `7017 ms` |
| Output | `{"category":"normal","confidence":0.95}` |
| Schema | `PASS` |
| Accounting | methodology-validation evidence only |

## Official warm evidence

| Metric | Evidence |
|---|---|
| Official warm requests | `20` |
| Valid warm outputs | `20/20` |
| Warm p50 | `2021 ms` |
| Warm p95 | `2214 ms` |
| Maximum warm latency | `7152 ms` |
| Approved p95 threshold | `<= 30000 ms` |
| Latency gate | `PASS` |

The accepted evidence states that all 20 official warm requests returned valid
structured output. The per-run records were preserved by the controlled
benchmark evidence capture; this closure records the accepted 20-run aggregate
without inventing per-run latency or output values not supplied to closure.

## Reliability

The official denominator is the original cold request plus the 20 official
warm requests. The corrected cold rerun is excluded:

`20 valid / 21 official normal requests = 95.24%`

Consequently, `PASS_FOR_DEVELOPMENT` is permanently unreachable for Stage
0.6.4 and the maximum classification is `PASS_WITH_LIMITATION`.
