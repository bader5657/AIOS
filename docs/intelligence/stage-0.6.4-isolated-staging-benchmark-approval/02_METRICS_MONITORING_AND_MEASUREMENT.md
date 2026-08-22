# Metrics, Monitoring, and Measurement

## Baseline and sampling

Before model load, record timestamped evidence for:

- host available RAM, swap used, load average, aggregate CPU utilization, and
  host responsiveness;
- staging filesystem total, used, and available bytes;
- container memory, memory+swap, CPU, PIDs, and cgroup memory events;
- `/api/ps` loaded-model state;
- `aios.service` ActiveState, SubState, MainPID, and NRestarts;
- PostgreSQL container health;
- exact Telegram poller count.

Sample container and host resource metrics once per second while any request is
active. Sample protected-service gates before every request, after every
request, and at least once every five seconds during a request. Preserve raw
timestamped samples; summaries alone are insufficient.

## Cold and warm metrics

For the cold request record request start, first observed model presence in
`/api/ps`, response completion, model load duration reported by Ollama, total
latency, prompt/eval counts and durations, schema result, peak container RAM,
peak host RAM consumption, peak CPU, host/container swap delta, and disk delta.

For each warm request record total latency, Ollama load/eval durations, result
classification, peak sampled memory/CPU, swap delta, and production gates.
Warm latency statistics use the `20` completed warm requests only:

- p50: nearest-rank value at rank `ceil(0.50 * 20) = 10` after ascending sort;
- p95: nearest-rank value at rank `ceil(0.95 * 20) = 19` after ascending sort.

Cold latency is reported separately and must not be mixed into warm percentiles.
Failed and timed-out normal samples remain in reliability counts and must not
be silently discarded; if latency is unavailable, report that sample as a
failure alongside the percentile denominator.

## RAM, CPU, swap, and disk controls

The container configuration must still enforce memory `3,221,225,472` bytes,
memory+swap `3,221,225,472` bytes, and `NanoCpus=1,000,000,000`. Verify the
effective cgroup values before execution. Any OOM event, limit breach, or
unexpected container restart is a failure.

Container swap must remain disabled by the equal memory and memory+swap limits.
Host swap is unacceptable when it increases by `64 MiB` or more above baseline
for three consecutive five-second samples, grows monotonically by `16 MiB` or
more across six consecutive samples, or coincides with material responsiveness
degradation. Any continuous unexplained growth is a stop condition even below
those reporting thresholds.

Record staging filesystem bytes before load, after the cold request, after all
requests, and after unload. Attribute model/runtime temporary and log growth.
Any unbounded growth, filesystem error, or less than `2 GiB` remaining is a
failure. No cleanup, prune, or deletion is authorized during measurement.

## Unload and recovery

After the final request, send no keep-alive override and allow the configured
`5m` keep-alive to expire. Poll `/api/ps` read-only until empty, with an unload
observation ceiling of `7m` after the final response. Record time-to-unload and
RAM recovery. Memory must return to within `256 MiB` of the pre-load container
baseline within two minutes after unload. Do not restart the container or any
production service to force recovery.
