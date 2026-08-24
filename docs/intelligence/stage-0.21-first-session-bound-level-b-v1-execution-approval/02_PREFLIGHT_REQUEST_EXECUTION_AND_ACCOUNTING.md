# Preflight, Request Execution, and Exact Accounting

## Fresh session preflight

Immediately before constructing the composition, verify and journal:

- source: `HEAD == main == origin/main`, clean worktree, exact frozen SHA, and
  exact module identities;
- privileged current firewall/NAT inspection: no public exposure, host `11434`
  listener, published port, acquisition network, or DNAT/public-ingress drift;
- AIOS active/running; freeze exact `MainPID`; require `NRestarts=0`;
- PostgreSQL healthy and exactly one Telegram poller;
- host `MemAvailable >= 2 GiB`; record swap baseline;
- one-minute load below available host CPU count;
- disk below 80% used and at least 5 GiB free;
- isolated staging Docker socket
  `unix:///opt/aios/runtime/intelligence/staging/ollama/mnt/docker.sock`;
- container running, not restarting, `OOMKilled=false`; freeze `RestartCount`;
- exact container ceilings: `Memory=3221225472`,
  `MemorySwap=3221225472`, `NanoCpus=1000000000`;
- runtime endpoint, Ollama version, model ID, config, schema binding,
  `keep_alive`, timeout, network, and IP.

Expected material runtime identity is endpoint `http://172.31.63.2:11434`,
Ollama `0.32.13`, model `qwen2.5:1.5b-instruct-q4_K_M`, `keep_alive=5m`, and
timeout `120000 ms`. Any failed, indeterminate, or materially drifted gate is
`FAILED_CLOSED` with no inference.

## Composition and request gates

Call repository `create_staging_composition(...)` exactly once. Reuse that
single composition, `AsyncClient`, client/provider lifecycle, and natural warm
state for both requests. Do not preload, force unload, or reconstruct between
requests.

Immediately before request 1, require `ACTIVE_SYNTHETIC`, request counter zero,
no request in progress, frozen source/config, same AIOS PID, `NRestarts=0`,
healthy PostgreSQL, exactly one Telegram poller, healthy unchanged container,
`MemAvailable >=2 GiB`, session swap growth at most 64 MiB, safe load and disk,
and unchanged network isolation. Increment `0 → 1` immediately before the
admitted Brain call.

Request 1 must finish completely before request 2 starts. Request 2's start
timestamp must be at least sixty seconds after request 1's start timestamp.
Immediately before request 2, repeat the complete lightweight request gate,
including unchanged source/config/runtime, AIOS PID and restart count,
PostgreSQL, Telegram poller, container `RestartCount`, OOM/restart state and
resource ceilings, host memory/swap/load/disk, network isolation, counter equal
to one, no active request, and valid spacing. Increment `1 → 2` immediately
before the second admitted Brain call.

## Per-request execution contract

For each request invoke exactly, once and in order:

1. repository projector;
2. repository mapper;
3. repository Brain boundary;
4. one underlying provider `/api/chat` inference.

No retry or fallback is permitted. Require `success=True`, `failure_code=None`,
the expected provider/model, preserved identifiers, exact structured-output
key set `{"result"}`, a string `result`, and repository schema validation
`PASS`.

If both requests succeed, exact totals are: projector 2, mapper 2, Brain
boundary 2, provider inference 2, `/api/chat` 2, request counter 2, retry 0,
fallback 0. Concurrency is one and queue capacity is one. The general session
ceiling remains five requests and thirty minutes, but this first-session
authority ends at exactly two. No third request is admissible.

For each request retain bounded observations of latency, container CPU,
container RAM and peak if available, host `MemAvailable`, swap, load, disk,
`RestartCount`, and OOM state. Approved read-only model-state evidence is
allowed, but observers must make no provider calls.

