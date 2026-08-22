# Monitoring and Early Stop Controls

## Continuous monitoring

Throughout all twenty requests, retain timestamped monitoring evidence for:

- container RAM and CPU;
- host `MemAvailable` and swap;
- staging disk health and available space;
- AIOS `MainPID` and `NRestarts`;
- PostgreSQL health;
- exact Telegram poller count.

Continue the existing approved sampling cadence: sample container and host
resources once per second while a request is active; check protected-service
gates before and after every request and at least once every five seconds
during a request. Monitoring must show that requests do not overlap.

## Immediate stop conditions

Stop immediately and send no further inference if:

- AIOS restarts, its `MainPID` changes, or `NRestarts` differs from zero;
- PostgreSQL becomes unhealthy;
- Telegram poller count differs from exactly one;
- host swap grows materially or sustainably under the existing approved swap
  thresholds;
- container memory reaches or exceeds `3 GiB`;
- the host becomes materially unresponsive or monitoring cannot continue;
- a normal request reaches `120000 ms`;
- repeated malformed output makes `20/21` impossible;
- staging disk becomes unhealthy, reports a filesystem error, grows without
  bound, or falls below the existing `2 GiB` free-space floor;
- any other production instability or existing Stage 0.6.4 stop condition
  occurs.

On stop, preserve all completed and in-flight evidence. Do not restart
services, alter limits, clean up, retry, replace a request, or improvise
remediation under this authority. Return the partial warm evidence for review.
