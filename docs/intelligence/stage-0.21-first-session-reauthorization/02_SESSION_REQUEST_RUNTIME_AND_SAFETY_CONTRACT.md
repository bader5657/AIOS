# Session, Request, Runtime, and Safety Contract

After Phase 0 passes and the new journal is exclusive-created, perform the
remaining fresh session preflight. Require clean synchronized
`HEAD == main == origin/main`; freeze the exact SHA and repository module
identities; require AIOS active/running with frozen `MainPID` and
`NRestarts=0`; healthy PostgreSQL; exactly one Telegram poller;
`MemAvailable >=2 GiB`; a frozen swap baseline without sustained pressure;
one-minute load below host CPU count; and disk below 80% used with at least
5 GiB free.

Using isolated Docker socket
`unix:///opt/aios/runtime/intelligence/staging/ollama/mnt/docker.sock`, require
container `aios-intelligence-ollama-staging` running, not restarting,
`OOMKilled=false`, frozen `RestartCount`, network `aios-ollama-runtime`, IP
`172.31.63.2`, and exact ceilings `Memory=3221225472`,
`MemorySwap=3221225472`, and `NanoCpus=1000000000`.

Freeze endpoint `http://172.31.63.2:11434`, Ollama `0.32.13`, model
`qwen2.5:1.5b-instruct-q4_K_M`, `keep_alive=5m`, timeout `120000 ms`, config,
schema binding, source, Docker socket, network, and IP. Material drift or any
failed/indeterminate gate is immediately `FAILED_CLOSED` without inference.

Create repository Stage 0.19 composition exactly once, yielding exactly one
`AsyncClient`, provider, invoker, receiver, and mapper lifecycle. Reuse all of
them across both requests. Do not preload, force unload, recreate the graph,
invoke Universal Ingestion, or perform real AIOSCore routing.

Admit exactly these requests in order:

1. `Temperature stable and vibration within normal range.`
2. `System pressure is stable and motor temperature remains within normal range.`

Each request must call repository `project_text_semantics`, use an exact
eligible prebuilt `CoreRouteResult`, call `composition.mapper`, pass its
`BrainInput` to `composition.brain_boundary`, and use repository schema
validation. Generate a fresh unique UUIDv4 correlation ID per request;
`CoreToBrainMapper` alone generates Brain request IDs. All four identifiers
must satisfy their required uniqueness and must not reuse Stage 0.20 or failed
session identifiers.

Immediately before each request, repeat the complete lightweight gate for
state, exact counter, no active request, frozen source/runtime, AIOS PID and
restart state, PostgreSQL, Telegram poller, container health/restart/OOM,
memory, swap growth no greater than 64 MiB, load, disk, and unchanged
lightweight network state. Increment `0 → 1` and then `1 → 2` exactly before
the corresponding admitted Brain call.

Request 1 must complete successfully before request 2. Request 2 may start
only at least sixty seconds after request 1's start and after its fresh gate
passes. Each request performs exactly one projector, mapper, Brain boundary,
provider inference, and `POST /api/chat`; requires success, no failure code,
expected provider/model, preserved IDs, exact structured key set `{"result"}`,
a string result, and repository schema validation `PASS`.

The reauthorized session limit is exactly two requests; no third request. The
unchanged general Level B ceiling is five requests or thirty minutes.
Concurrency and queue capacity are one. Retry and fallback are zero. Natural
warm reuse is allowed between requests.

