# Execution Safety, Resources, and Stop Controls

## Immutable runtime boundary

- endpoint: `http://172.31.63.2:11434`, isolated staging/private network only
- model: `qwen2.5:1.5b-instruct-q4_K_M`
- Ollama RAM ceiling: 3 GiB
- inference CPU ceiling: 1 vCPU
- concurrency: 1
- queue: 1
- retry: NONE
- fallback: NONE

The operator must not restart Ollama, pull or replace a model, preload a model at AIOS boot, reconnect an acquisition network, publish a port, modify a firewall, change container configuration, modify staging storage, or force unload. Existing `keep_alive=5m` behavior is preserved. Optional post-request model observation is read-only and is not an unload benchmark.

## Mandatory preflight

Before the request, record and require:

- `aios.service` active/running and `NRestarts=0`;
- PostgreSQL healthy;
- exactly one Telegram poller;
- responsive host;
- stable swap with no meaningful growth;
- safe staging filesystem capacity;
- staging container within the 3 GiB RAM and 1 vCPU ceilings;
- concurrency/queue controls unchanged;
- private staging attachment and absence of public/host port exposure unchanged;
- adapter/config/model identities match this package.

Any failed or indeterminate preflight check stops execution before inference.

## Request controls

- Make exactly one adapter invocation and one inference POST.
- Do not run a loop, benchmark, retry, fallback, or manual repeat.
- Do not invoke production Brain, Core, Telegram, Registry, Event, Memory, Specialist, or business flows.
- Do not modify repository, runtime, VPS, network, services, dependencies, or databases.

## Mandatory postflight

Whether the request succeeds or fails, record the same safety observations after it and confirm:

- AIOS remains active with `NRestarts=0`;
- PostgreSQL remains healthy;
- exactly one Telegram poller remains;
- host responsiveness and swap remain stable;
- filesystem remains safe;
- container remains within the approved ceilings;
- network exposure is unchanged;
- no production or service mutation occurred.

If the request fails, do not retry. Preserve the adapter's bounded failure metadata and the postflight safety evidence for governance review.
