# Proposed Staging Topology and Controls

This topology is evaluated and reserved for later approval. It is not active
while the provenance gate is blocked.

## Identity, storage, and lifecycle

| Control | Proposed exact value |
|---|---|
| Container | `aios-intelligence-ollama-staging` |
| Image | `ollama/ollama:0.32.13` |
| Platform/digest | `linux/amd64` / `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` |
| Runtime root | `/opt/aios/runtime/intelligence/staging/ollama` |
| Model host path | `/opt/aios/runtime/intelligence/staging/ollama/models` |
| Model container path | `/var/lib/ollama/models` |
| Docker configuration | `/opt/aios/runtime/intelligence/staging/ollama/config` |
| Disk bound | exactly `16 GiB` (`17,179,869,184 bytes`) |

The runtime root is a separately bounded filesystem or quota-controlled mount,
outside `/opt/aios-src`. The model path is an explicit bind mount within that
bound. Ollama's uncontrolled default host storage is prohibited. The container
has an independent manual lifecycle, no automatic restart, no boot dependency,
and no dependency from `aios.service`, PostgreSQL, or Telegram polling.

## Resource and network controls

| Control | Proposed exact value |
|---|---|
| Memory hard limit | `3 GiB` |
| CPU maximum | `1 vCPU equivalent` |
| Active inference | exactly `1` |
| Pending queue | at most `1` |
| Loaded models | exactly `1` |
| Timeout ceiling | `120000 ms` at the later caller/benchmark boundary |
| Host publication | `127.0.0.1:11434:11434/tcp` only |
| Container bind | `OLLAMA_HOST=0.0.0.0:11434` inside the isolated namespace |
| Public exposure | `NONE` |
| Privilege | no `--privileged`, host PID/network namespace, devices, or Docker socket |

Loopback publication is selected because it is the simplest bounded path for a
later local provider-adapter test. It does not use host networking. Egress is
allowed only during separately approved pinned image/model acquisition and is
disabled or restricted after digest verification, before benchmark runtime use
where practical.

## User, permissions, secrets, and environment

The pinned official image has no declared non-root `USER` and therefore runs as
UID 0 by default. Stage execution must first validate an explicit
`--user 65532:65532` override against the pinned image without weakening any
other boundary. Proposed host ownership is `65532:65532`; runtime root and
model directory modes are `0750`; created regular files must not be
world-writable. If non-root compatibility cannot be established, execution
stops for a separate risk decision—root-in-container is not silently accepted.

No production secrets are required or mounted. In particular, `runtime.env`,
Telegram tokens, database credentials, SSH keys, and production secret paths
are prohibited.

Minimum proposed environment:

- `OLLAMA_MODELS=/var/lib/ollama/models`;
- `OLLAMA_HOST=0.0.0.0:11434`;
- `OLLAMA_MAX_LOADED_MODELS=1`;
- `OLLAMA_NUM_PARALLEL=1`;
- `OLLAMA_MAX_QUEUE=1`;
- `OLLAMA_KEEP_ALIVE=5m`.

No model is preloaded. A benchmark request may load the single model; it is
unloaded after five minutes of bounded idle time or explicitly unloaded. A
bounded readiness check uses `GET /api/version` over loopback and does not load
a model. Runtime readiness is not model-quality success.
