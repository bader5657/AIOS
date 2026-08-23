# Source, Runtime, Resource, and Protection Controls

## Exact source authority

Create a new detached clean temporary checkout at:

`/opt/aios/runtime/intelligence/staging/stage-0.13-src`

It must resolve exactly to
`512bb81469215faa1004b56da03e0b32a28d58b6`. Production checkout
`/opt/aios-src` remains unchanged. Stage 0.8 and Stage 0.10 temporary sources
must not be reused, modified, or deleted.

Immediately before execution, use `/opt/aios/runtime/venv/bin/python` without
package installation and prove `httpx==0.28.1`. Explicit real-path checks must
show `core.brain.input_contracts`, `core.brain.receiver`,
`core.brain.inference`, `core.brain.inference_contracts`, and
`core.brain.providers.ollama` all load from the Stage 0.13 checkout. Mixed
imports or a dirty/wrong-SHA checkout stop execution.

Record production and temporary checkout SHAs/cleanliness before and after the
request. Neither source may change.

## Immutable staging runtime

| Control | Required value |
|---|---|
| Ollama | `0.32.13` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Endpoint | `http://172.31.63.2:11434` |
| RAM | `3 GiB` |
| CPU | `1 vCPU` |
| Concurrency | `1` |
| Queue | `1` |
| Retry | `NONE` |
| Fallback | `NONE` |

No restart, model pull/replacement, forced unload, keep-alive change,
acquisition-network reconnection, public port, firewall/configuration change,
resource expansion, container mutation, or runtime lifecycle action is
authorized. Model unloaded state is preferred if naturally observed but must
not be forced.
