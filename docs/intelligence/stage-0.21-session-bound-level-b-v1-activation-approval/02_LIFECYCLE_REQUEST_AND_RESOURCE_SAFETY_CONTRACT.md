# Lifecycle, Request, and Resource Safety Contract

## Frozen lifecycle

`INACTIVE → PREFLIGHT → ACTIVE_SYNTHETIC → STOPPING → CLOSED`

Failure from `PREFLIGHT` or `ACTIVE_SYNTHETIC` transitions to
`FAILED_CLOSED`. There is no automatic restart, recovery to active, or session
extension. Admission ends after five requests or thirty minutes from session
start, whichever occurs first.

One Stage 0.19 composition is constructed after a passing preflight and reused
for the session. It owns one AsyncClient and one OllamaInferenceProvider. The
composition/client is closed exactly once during shutdown, cancellation, or
failure. It is not recreated between successful requests; invalid composition
state fails the session closed.

Natural model warm reuse is permitted with `keep_alive=5m`. Preload, manual
load, forced unload, pull, model change, and active lifecycle management are
prohibited.

## Request admission and execution

| Control | Frozen value |
|---|---|
| Maximum requests | `5` |
| Maximum duration | `30 minutes` |
| Concurrency | `1` |
| Queue capacity | `1` pending request |
| Retry | `NONE` |
| Fallback | `NONE` |
| Timeout ceiling | `120000 ms` per request |
| Start-time spacing | at least `60 seconds` |

No request overlaps another. A subsequent request is admitted only when the
previous request has fully completed, its start timestamp is at least sixty
seconds after the previous start timestamp, and the next safety gate passes.
No extra sixty-second post-completion delay is required when start timestamps
already satisfy the interval.

Each admitted request uses only:

`project_text_semantics → eligible prebuilt CoreRouteResult → composition.mapper → BrainInput → composition.brain_boundary → repository schema validation → InferenceResult`

Universal Ingestion, real AIOSCore routing, production ingress, and direct
provider calls are prohibited. Correlation IDs are unique and contract-valid.
The composition mapper remains sole owner of a unique Brain request ID. Stage
0.20 fixed IDs must not be reused.

Continuation requires success, no failure code, exact provider/model and IDs,
a Mapping structured output, and passing repository schema validation.

## Safety cadence

Session preflight freezes clean source SHA and module identities, Ollama/model/
endpoint/provider configuration, schema binding, timeout, keep-alive, staging
socket/network/IP, and container ceilings. It also requires the approved
privileged read-only firewall/NAT inspection; no exposure, publication,
listener, acquisition network, or ingress drift; stable AIOS; healthy
PostgreSQL; one Telegram poller; safe RAM, swap, load, and disk; and a healthy
container with frozen restart count.

Before every request require the pinned identity, same nonzero AIOS MainPID and
`NRestarts=0`, healthy PostgreSQL, exactly one Telegram poller, healthy
container and unchanged ceilings/restart count, MemAvailable at least 2 GiB,
session swap growth at most 64 MiB without sustained pressure, one-minute load
below available CPU count, disk below 80% used with at least 5 GiB free, no
11434 host listener/published port/acquisition network, free request capacity,
valid spacing, and no request in progress.

Observe RAM, swap, load, disk, container OOM/restart, and production health
during each request without provider calls. Apply the same lightweight safety
gate after each request. Session postflight additionally proves source and
configuration preservation, stable production, network isolation, exact
request/provider/HTTP counts, and deterministic composition/client cleanup.
