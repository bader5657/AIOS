# Session Execution and Safety Contract

A completely new ID matching
`stage-0.21-level-b-session-YYYYMMDDTHHMMSSffffffZ-<uuid4hex>` and a new
exclusive journal at
`/opt/aios/runtime/intelligence/staging/level-b-sessions/<session_id>.jsonl` are
required. Prior journals remain immutable and may not be reused. Collision is a
hard stop with no alternate attempt under this authority.

Exactly two synthetic requests are authorized, with no third:

1. `Temperature stable and vibration within normal range.`
2. `System pressure is stable and motor temperature remains within normal range.`

The general Level B ceiling remains 5; this authority is narrower at 2. Session
duration is at most 30 minutes, concurrency and queue are `1`, retry and
fallback are none, and timeout is `120000 ms/request`. Request 2 starts at least
60 seconds after request 1 starts, after request 1 completes and a fresh gate
passes.

Full fresh preflight after journal creation must verify clean synchronized
source; AIOS active/running with frozen `MainPID` and `NRestarts=0`; healthy
PostgreSQL; exactly one Telegram poller; at least 2 GiB available RAM; frozen
swap baseline; safe load; disk below 80% used with at least 5 GiB free; healthy
staging container without restart/OOM; and exact resource/runtime/config pins.

The staging identity is Docker socket
`unix:///opt/aios/runtime/intelligence/staging/ollama/mnt/docker.sock`, container
`aios-intelligence-ollama-staging`, network `aios-ollama-runtime`, IP
`172.31.63.2`, endpoint `http://172.31.63.2:11434`, Ollama `0.32.13`, model
`qwen2.5:1.5b-instruct-q4_K_M`, keep-alive `5m`, Memory and MemorySwap
`3221225472`, and NanoCpus `1000000000`.

Create one repository Stage 0.19 composition, AsyncClient, provider, invoker,
receiver, and mapper. Reuse the lifecycle for both requests. Natural warm reuse
is allowed; preload, forced unload, and recreation are prohibited.

Each request follows `project_text_semantics → eligible prebuilt CoreRouteResult
→ composition.mapper → BrainInput → composition.brain_boundary → repository
validate_schema → InferenceResult`. Universal Ingestion and production Core
routing are prohibited.

Before each request, verify unchanged authoritative interpreter, source/module
identities, AIOS PID/runtime/config, zero service/container restarts, healthy
PostgreSQL/container, one poller, no OOM, RAM at least 2 GiB, swap growth at most
64 MiB, safe load/disk, unchanged lightweight network, no overlap, and the
expected request counter. Any failure is `FAILED_CLOSED`.

Successful totals are projector, mapper, Brain, provider, and `/api/chat` each
2; request counter 2; retry and fallback 0. Postflight repeats identity, health,
resource, network, accounting, and cleanup checks; closes composition/client
exactly once; and reaches `CLOSED` only if all checks pass.

The journal is append-only JSONL, flushed and fsynced for every event. Finalize
once by appending the final record, flushing, fsyncing, closing, and computing
SHA-256; never reopen it for mutation.

Authorized runtime mutation is limited to one temporary `/tmp` harness and one
new session journal. Package/environment installation, persistent `PYTHONPATH`,
source, sudo, firewall/network, Docker, service, model, and production-config
mutation are prohibited. Only synthetic data is allowed; real user/business
data and Level C are prohibited; Universal Ingestion remains inactive.

