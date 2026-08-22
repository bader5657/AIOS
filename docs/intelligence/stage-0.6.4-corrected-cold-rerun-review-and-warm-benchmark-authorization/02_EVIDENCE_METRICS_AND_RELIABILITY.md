# Evidence, Metrics, and Reliability

## Mandatory per-run record

For each of the twenty requests preserve and report:

- run number;
- HTTP status;
- total latency in milliseconds;
- unmodified structured content;
- schema-valid `yes` or `no`;
- timeout status;
- runtime-failure status.

Invalid, malformed, failed, and timed-out results remain evidence. Do not
coerce, repair, reinterpret, retry, replace, or discard them.

## Warm latency

After the warm sequence, report the twenty warm-request latencies in ascending
order. Calculate warm-only nearest-rank percentiles as follows:

- p50 is sorted rank `10`;
- p95 is sorted rank `19`.

Do not include either the original cold result or corrected cold rerun in the
sorted list or percentile calculation. The existing warm p95 acceptance gate
remains unchanged.

## Official reliability accounting

The official denominator remains exactly `21` normal requests:

1. the permanently retained, invalid original cold request; and
2. the twenty official warm requests authorized here.

If every warm result is valid, official reliability is `20/21` (`95.24%`). It
is lower for every invalid warm result. The corrected cold rerun is reported
separately as methodology-validation evidence and never substitutes into this
denominator.

Because the original cold result is invalid, `PASS_FOR_DEVELOPMENT` is
unreachable. `PASS_WITH_LIMITATION` remains possible only if all twenty warm
requests are valid, p95 and every safety gate pass, and separately authorized
timeout, malformed-output, unload, and recovery gates later pass.
