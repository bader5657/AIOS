# Option C Resource and Policy Decision

## Selected runtime and model

The Project Owner selects `OPTION C` and retains:

- Ollama `0.32.13`, `linux/amd64`;
- image digest `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b`;
- Qwen2.5 1.5B Instruct `Q4_K_M`, approximately `986 MB`;
- local, isolated, staging-first execution strategy.

This decision does not switch to llama.cpp and does not select a smaller model
solely because acquisition failed under the former disk ceiling.

## Changed ceiling

| Resource | Previous | Approved |
|---|---:|---:|
| Staging runtime/model/temporary disk | `6 GiB` (`6,442,450,944 bytes`) | `16 GiB` (`17,179,869,184 bytes`) |

`STAGING_RUNTIME_MODEL_TEMP_DISK_CEILING = 17179869184`

The 16 GiB ceiling is a hard maximum for the isolated staging acquisition and
benchmark environment. It is not an increase to total VPS capacity and must
not be interpreted as a reservation or permission to consume host safety
reserve.

Before allocation and throughout the authorized operation, the host filesystem
must retain at least `10 GiB` or `15%` of its total capacity, whichever is
larger. Allocation must not proceed, and an active operation must stop safely,
if that reserve cannot remain available.

## Unchanged ceilings and policies

| Control | Unchanged value |
|---|---|
| RAM hard limit | `3 GiB` |
| CPU ceiling | `1 vCPU equivalent` |
| Model artifact ceiling | `2 GiB` |
| Concurrent inference | exactly `1` |
| Pending queue | `1` |
| Timeout ceiling | `120000 ms` |
| Loaded models | exactly `1` |
| Providers | exactly `1` |
| Retry | `NONE` |
| Fallback | `NONE` |
| Dynamic routing | `NONE` |

The disk increase waives none of these controls and provides no evidence that
Ollama or Qwen is suitable for production.
