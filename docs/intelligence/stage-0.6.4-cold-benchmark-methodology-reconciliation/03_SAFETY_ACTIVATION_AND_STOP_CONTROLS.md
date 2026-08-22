# Safety Activation and Stop Controls

## Reconciliation post-cold evidence

Read-only observations collected before activation established:

| Gate | Observation | Result |
|---|---|---|
| AIOS | `active/running`; MainPID `15845` | `PASS` |
| Restarts | `NRestarts=0` | `PASS` |
| PostgreSQL | `aios-postgres` healthy | `PASS` |
| Telegram | exactly one poller process, PID `15845` | `PASS` |
| Host | responsive; load average `0.20, 0.08, 0.11` | `PASS` |
| Host swap | `512 KiB` unchanged across seven 5-second samples; `si=0`, `so=0` | `PASS` |
| Container | running; `OOMKilled=false`; restart count `0`; `667.5 MiB / 3 GiB` | `PASS` |
| Ceilings | memory and memory+swap `3,221,225,472`; CPU `1 vCPU` | `PASS` |
| Isolation | only internal `aios-ollama-runtime`; no published ports | `PASS` |
| Staging disk | `/dev/loop0`; `10,715,889,664` bytes available; `36%` used | `PASS` |

These delayed observations do not fabricate the samples missed when the first
cold shell exited. The original evidence gap remains recorded. They establish
the safety precondition for the separately approved corrected rerun.

## Activation gate

Immediately before the rerun, the operator must reconfirm read-only that AIOS
is active/running with unchanged MainPID and `NRestarts=0`, PostgreSQL is
healthy, exactly one Telegram poller exists, the host is responsive, swap is
not growing, the container is within its ceilings without OOM/restart, and the
staging disk remains healthy with at least `2 GiB` available.

Any failed or unavailable preflight observation blocks activation. During and
after the rerun, retain the monitoring and immediate-stop controls of the
original Stage 0.6.4 approval. On any stop condition, send no more inference.
