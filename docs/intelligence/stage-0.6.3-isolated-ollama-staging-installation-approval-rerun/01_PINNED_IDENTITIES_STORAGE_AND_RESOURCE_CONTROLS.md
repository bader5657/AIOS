# Pinned Identities, Storage, and Resource Controls

## Immutable runtime and model

| Field | Approved exact value |
|---|---|
| Runtime | `ollama/ollama:0.32.13` |
| Platform | `linux/amd64` |
| Runtime digest | `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Model manifest | `sha256:65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` |
| Model blob | `sha256:183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` |
| Blob size | `986,048,512 bytes` |
| Quantization/license | `Q4_K_M` / Apache-2.0 |

No `latest`, floating replacement, second model, retry, fallback, or dynamic
routing is permitted. Acquisition must stop before acceptance if any platform,
manifest, blob, size, quantization, or license identity differs.

## Exact staging storage

| Control | Approved exact value |
|---|---|
| Container | `aios-intelligence-ollama-staging` |
| Runtime root | `/opt/aios/runtime/intelligence/staging/ollama` |
| Model host path | `/opt/aios/runtime/intelligence/staging/ollama/models` |
| Model container path | `/var/lib/ollama/models` |
| Configuration path | `/opt/aios/runtime/intelligence/staging/ollama/config` |
| Disk hard ceiling | `16 GiB` (`17,179,869,184 bytes`) |
\nExact enforcement value: `17179869184 bytes`.

The runtime root must be a separately hard-bounded filesystem or enforceable
quota allocation. All assets remain outside `/opt/aios-src`. Only the exact
model host path may be mounted for model persistence; uncontrolled default host
storage and arbitrary host mounts are prohibited.

Before allocation and throughout installation, the host must retain at least
`max(10 GiB, 15% of host filesystem capacity)`. Production Docker capacity
must remain safe. Failure to prove either condition is a hard stop.

## Unchanged resource controls

| Control | Approved value |
|---|---|
| Memory hard limit | `3 GiB` |
| CPU maximum | `1 vCPU equivalent` |
| Model-file ceiling | `2 GiB` |
| Active inference | exactly `1` |
| Pending queue | at most `1` |
| Loaded models | exactly `1` |
| Caller/benchmark timeout | `120000 ms` |
| Retry/fallback/dynamic routing | `NONE / NONE / NONE` |
