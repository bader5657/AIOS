# Safety, Stop, Classification, and Production Boundary

## Fresh preflight and safety checks

Before the timeout request and after each inference-related test, capture the
existing Stage 0.6.4 production and resource gates: container health and
resource state, host responsiveness and swap, staging filesystem state,
`aios.service` state and `NRestarts`, PostgreSQL health, and exact Telegram
poller count.

## Immediate stop conditions

Stop immediately, send no further inference, and preserve evidence if:

- AIOS restarts, becomes inactive, or `NRestarts` differs from zero;
- PostgreSQL becomes unhealthy;
- Telegram poller count differs from exactly one;
- host swap grows materially under existing approved thresholds;
- the container exceeds a resource ceiling;
- the staging disk becomes unsafe;
- the host becomes materially unresponsive; or
- the container or runtime crashes unexpectedly.

On stop, do not retry, widen a limit, switch a model, restart production
services, or improvise remediation under this authority. Apply the existing
Stage 0.6.4 `FAIL` authority.

## Classification

If all three special-test gates pass and the accepted warm evidence remains
valid, the final Stage 0.6.4 classification is `PASS_WITH_LIMITATION`. The
explicit limitation is the permanently retained original cold schema-invalid
result, yielding official reliability of `20/21` (`95.24%`).

If any safety, resource, containment, timeout/recovery, unload, or memory
recovery gate fails, classify according to the existing Stage 0.6.4 `FAIL`
authority.

## Production boundary

Even `PASS_WITH_LIMITATION` authorizes only continued isolated Intelligence
development under the current KVM2 constraints. It does not authorize
production inference, Brain integration, provider-adapter activation,
production traffic, business use, deployment, or startup automation.
