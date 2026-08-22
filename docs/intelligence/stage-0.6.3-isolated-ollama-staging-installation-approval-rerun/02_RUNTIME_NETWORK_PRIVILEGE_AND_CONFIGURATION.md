# Runtime, Network, Privilege, and Configuration

## Lifecycle and network

The container has an independent manual lifecycle with no automatic restart or
host-boot integration. It has no dependency from `aios.service`, PostgreSQL,
Telegram polling, or any production workload.

Approved network topology:

- Docker publishes only `127.0.0.1:11434:11434/tcp` on the host;
- `OLLAMA_HOST=0.0.0.0:11434` is used only inside the isolated container
  namespace so Docker loopback port forwarding can reach the service;
- host bind `0.0.0.0:11434`, host networking, and any public endpoint are
  prohibited;
- outbound access is temporary and limited to pinned image acquisition and the
  exact approved model acquisition;
- after digest verification, generic long-term outbound access is removed or
  restricted before local staging use where practical.

## Runtime user and filesystem permissions

The pinned `v0.32.13` image Dockerfile declares no `USER`. Non-root UID
`65532:65532` compatibility has not been proven and is not invented by this
approval. The approved staging fallback is UID/GID `0:0` inside the container,
contained by all of the following mandatory boundaries:

- no privileged mode;
- no host PID, IPC, or network namespace and no explicit `--userns=host`;
- no Docker socket, device, production secret, or arbitrary host mount;
- only bounded staging mounts;
- no public exposure;
- `no-new-privileges` and all Linux capabilities dropped.

The runtime root, model path, and config path are owned `root:root` and use mode
`0750`. Regular files must not be world-writable. Production directories must
not be chmod/chown modified. A later non-root migration requires separate
compatibility evidence and governance; it is not required for this staging-only
approval.

## Secrets and minimum environment

Mounted secrets: `NONE`. `runtime.env`, Telegram tokens, PostgreSQL
credentials, SSH keys, API keys, and production secret paths are prohibited.

Exact minimum environment, verified as supported by Ollama `v0.32.13` source:

- `OLLAMA_MODELS=/var/lib/ollama/models`;
- `OLLAMA_HOST=0.0.0.0:11434` inside the container only;
- `OLLAMA_MAX_LOADED_MODELS=1`;
- `OLLAMA_NUM_PARALLEL=1`;
- `OLLAMA_MAX_QUEUE=1`;
- `OLLAMA_KEEP_ALIVE=5m`.

No unrelated tuning variable is approved. Source verification:
`https://github.com/ollama/ollama/blob/v0.32.13/envconfig/config.go`.

## Loading and health

Model preload is prohibited during host boot, AIOS startup, PostgreSQL startup,
container creation, and runtime readiness checks. The model loads only during a
later authorized benchmark/inference invocation and unloads after the bounded
five-minute idle period or an explicit unload.

Runtime health is a bounded `GET /api/version` over the loopback endpoint. It
must not load a model. PASS proves only that the pinned Ollama runtime responds;
it does not prove model loading, inference quality, resource fit, or production
readiness.
