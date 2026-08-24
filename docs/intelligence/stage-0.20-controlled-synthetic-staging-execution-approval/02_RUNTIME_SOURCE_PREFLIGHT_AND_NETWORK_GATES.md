# Runtime, Source, Preflight, and Network Gates

Immediately before the sole request, require and retain all of these exact
runtime controls:

| Control | Required value |
|---|---|
| Ollama | `0.32.13` |
| Endpoint | `http://172.31.63.2:11434` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Timeout ceiling | `120000 ms` |
| Keep-alive | `5m` |
| Memory / memory-swap | `3221225472 / 3221225472` bytes |
| CPU | `NanoCpus=1000000000` |
| Concurrency / queue | `1 / 1` |

Stop before inference on any material mismatch. The model must be naturally
unloaded immediately before execution; read-only `/api/ps` or its approved
local CLI equivalent must report no loaded model. Never force unload.

The exact clean repository checkout, branch/detached state, SHA, porcelain
status, and resolved module paths for Stage 0.17, Stage 0.18, and Stage 0.19
must be retained. Mixed imports, dirty source, wrong SHA, or production source
mutation stops execution.

AIOS must be active/running with one stable nonzero MainPID and `NRestarts=0`.
PostgreSQL must be healthy without restart degradation. Exactly one
`core.adapters.telegram.main` poller must exist.

Host MemAvailable must be at least 2 GiB. Record swap before execution; growth
through postflight must be at most 64 MiB without sustained pressure. The host
must be responsive and one-minute load below available host CPU count.
Staging disk usage must be below 80% with at least 5 GiB free.

The Ollama container must be running, not restarting, not OOM-killed, and
within the frozen limits. Its only attachment is the internal
`aios-ollama-runtime` network; no acquisition network, published host port,
public listener, temporary firewall/NAT rule, or exposure drift is allowed.
Endpoint identity inspection must not add a provider health request.

All gates run immediately before the request, with no unrelated intervening
work. A failed or indeterminate gate stops execution.
