# Runtime, Resource, Preflight, and Postflight Controls

## Immutable runtime boundary

| Control | Required value |
|---|---|
| Ollama | `0.32.13` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Endpoint | `http://172.31.63.2:11434` |
| RAM ceiling | `3 GiB` |
| CPU ceiling | `1 vCPU` |
| Concurrency | `1` |
| Queue | `1` |
| Retry | `NONE` |
| Fallback | `NONE` |

The existing verified isolated runtime is authoritative. Do not restart
Ollama, pull or replace a model, reconnect acquisition networking, change
keep-alive, force unload, alter limits, publish a port, or modify container,
network, firewall, configuration, or staging storage. Initial model-loaded
state may be observed read-only if practical; it is not a reason to force an
unload.

## Mandatory immediate preflight

Before the one invocation, record and require:

- `/opt/aios-src` remains at its recorded SHA and is unchanged;
- Stage 0.10 checkout is clean at the exact required SHA;
- adapter and invoker modules load from the Stage 0.10 checkout;
- `httpx==0.28.1`;
- AIOS active/running with `NRestarts=0`;
- PostgreSQL healthy;
- exactly one Telegram poller;
- Ollama staging healthy;
- model loaded state observed if practical, without lifecycle action;
- stable swap and responsive host;
- safe staging disk capacity;
- private-only Ollama attachment with no public/host exposure; and
- runtime limits, concurrency, and queue unchanged.

Any failed or indeterminate mandatory preflight item stops execution before
inference.

## One-request and failure controls

After a passing preflight, send exactly one invocation. There is no health
preflight through the adapter, ordinary second request, retry, fallback,
alternate provider/model, loop, or benchmark. A failed `InferenceResult` is
recorded with its exact `FailureCode` and is not retried. An unexpected
exception is preserved for governance classification and is not retried.

## Mandatory postflight

Whether success, failed result, cancellation, or exception occurs, immediately
verify and record:

- AIOS remains active and `NRestarts=0`;
- PostgreSQL remains healthy;
- exactly one Telegram poller remains;
- swap remains stable and host responsive;
- Ollama remains within `3 GiB` and the existing CPU ceiling;
- staging disk remains safe;
- production source and temporary source remain unchanged; and
- no network, firewall, configuration, runtime, service, container, database,
  or production mutation occurred.
