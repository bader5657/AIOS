# AIOS Intelligence Stage 0.6.4 — Corrected Cold Rerun Review and Warm Benchmark Authorization

| Control | Decision |
|---|---|
| Work type | `GOVERNANCE / EVIDENCE REVIEW / WARM AUTHORIZATION` |
| Original cold | `CONTAINED_INVALID_RESULT`; permanently retained |
| Corrected cold rerun | `PASS` |
| Corrected cold HTTP / latency | `200` / `7017 ms` |
| Corrected cold content | `{"category":"normal","confidence":0.95}` |
| Corrected cold schema | `PASS` |
| Official reliability denominator | exactly `21`: original cold plus twenty official warm requests |
| Maximum classification | `PASS_WITH_LIMITATION` |
| Warm authority | exactly twenty controlled sequential requests |
| Later special-test authority | `NONE` in this activation |
| Production authority | `NONE` |

The corrected rerun validates the clarified prompt methodology. It does not
replace, repair, or remove the invalid original cold observation and does not
enter the official reliability denominator or warm latency percentiles.
`PASS_FOR_DEVELOPMENT` is therefore no longer reachable. The best possible
normal-result reliability is `20/21` (`95.24%`).

The supplied post-rerun evidence establishes a safe review state: container
memory was approximately `1.68 GiB / 3 GiB`, host swap approximately `512 KiB`
and stable, the model remained loaded, AIOS was active/running with
`NRestarts=0`, PostgreSQL was healthy, exactly one Telegram poller existed,
staging disk was healthy, the host was responsive, and no production
instability was observed.

This package authorizes no inference while it is authored, reviewed, or
published.

`STAGE 0.6.4 WARM BENCHMARK APPROVED — READY FOR 20 CONTROLLED WARM RUNS`
