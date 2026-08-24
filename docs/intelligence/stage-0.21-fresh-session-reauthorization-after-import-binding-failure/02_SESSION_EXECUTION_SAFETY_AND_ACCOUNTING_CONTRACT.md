# Session Execution, Safety, and Accounting Contract

The new ID must match
`stage-0.21-level-b-session-YYYYMMDDTHHMMSSffffffZ-<uuid4hex>`. Its journal is
exclusive-created at
`/opt/aios/runtime/intelligence/staging/level-b-sessions/<new_session_id>.jsonl`.
A collision stops the attempt with no alternate retry under this authority.

Exactly these two synthetic requests are authorized, with no third request:

1. `Temperature stable and vibration within normal range.` with provenance
   `stage-0.21-session-request-1` and context references `()`.
2. `System pressure is stable and motor temperature remains within normal range.`
   with provenance `stage-0.21-session-request-2` and context references `()`.

The general Level B ceiling remains 5; this authority is narrower at 2.
Maximum duration is 30 minutes, concurrency and queue are `1`, retry and
fallback are none, and timeout is `120000 ms/request`. Request 2 may start only
at least 60 seconds after request 1 starts, after request 1 fully completes and
its fresh request-2 gate passes.

Fresh preflight after journal creation must verify AIOS active/running with
frozen `MainPID` and `NRestarts=0`; healthy PostgreSQL; exactly one Telegram
poller; `MemAvailable >= 2 GiB`; frozen swap baseline without sustained
pressure; one-minute load below available CPU count; disk below 80% used with
at least 5 GiB free; and the healthy pinned staging container through
`unix:///opt/aios/runtime/intelligence/staging/ollama/mnt/docker.sock`.

The staging container must be `aios-intelligence-ollama-staging`, use network
`aios-ollama-runtime` and IP `172.31.63.2`, be running and neither restarting
nor OOM-killed, and freeze `RestartCount`. Ceilings are memory and memory-swap
`3221225472` and NanoCpus `1000000000`.

Runtime pins are endpoint `http://172.31.63.2:11434`, Ollama `0.32.13`, model
`qwen2.5:1.5b-instruct-q4_K_M`, keep-alive `5m`, timeout `120000 ms`, repository
schema binding, Docker socket, network/IP, and resource ceilings. Material drift
is `FAILED_CLOSED`.

Create the Stage 0.19 composition exactly once with composition, client,
provider, invoker, receiver, and mapper counts each equal to 1, and reuse that
lifecycle across both requests. Natural warm reuse is allowed; preload, forced
unload, or recreation is prohibited.

Each request follows `project_text_semantics` to an eligible prebuilt
`CoreRouteResult`, composition mapper, `BrainInput`, composition Brain boundary,
repository `validate_schema`, and `InferenceResult`. Universal Ingestion and
real Core routing are prohibited. Each request gets a distinct UUIDv4
correlation ID; only the mapper generates its distinct Brain request ID.

Immediately before each admission, the gate verifies active state and expected
counter, no active request, unchanged source/module and runtime/config identity,
same AIOS PID, zero restarts, healthy PostgreSQL and container, exactly one
poller, unchanged container restart count, RAM, swap growth no more than 64 MiB,
safe load/disk, and unchanged lightweight network evidence. Increment the
counter `0→1` or `1→2` immediately before Brain admission.

Each admitted request performs exactly one projector, mapper, Brain boundary,
provider, and `/api/chat` call with no retry or fallback. It must return
`success=True`, `failure_code=None`, the pinned provider/model, preserved IDs,
and schema-valid structured output with exactly key `{"result"}` whose value is
a string. Any failure is `FAILED_CLOSED`; request 1 failure prohibits request 2.

Successful totals are projector, mapper, Brain, provider, and `/api/chat` each
2; request counter 2; retry and fallback 0. Postflight transitions
`ACTIVE_SYNTHETIC → STOPPING`, repeats system, source/module, container,
resource, network, and accounting checks, and closes composition/client exactly
once. All-pass transitions to `CLOSED`; otherwise `FAILED_CLOSED`.

The journal is append-only JSONL with flush/fsync per event. Finalization appends
the final record, flushes, fsyncs, closes, computes SHA-256, and never reopens it
for mutation.

