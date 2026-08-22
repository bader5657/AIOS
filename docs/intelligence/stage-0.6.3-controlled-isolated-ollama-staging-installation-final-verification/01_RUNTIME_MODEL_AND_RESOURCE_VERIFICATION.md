# Runtime, Model, and Resource Verification

## Isolated daemon and runtime identity

The staging daemon is a separate `dockerd` using:

- data root: `/opt/aios/runtime/intelligence/staging/ollama/mnt/docker-root`;
- exec root: `/opt/aios/runtime/intelligence/staging/ollama/mnt/docker-exec`;
- socket: `/opt/aios/runtime/intelligence/staging/ollama/mnt/docker.sock`;
- `--bridge=none --iptables=false --ip6tables=false --ip-forward=false
  --ip-masq=false --userland-proxy=false`.

Read-only image/container inspection returned:

| Field | Verified value | Result |
|---|---|---|
| Runtime | `Ollama 0.32.13` | `PASS` |
| Platform | `linux/amd64` | `PASS` |
| Repo digest | `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` | `PASS` |
| Local image ID | `sha256:ff2cfdc6b5c8d5ac07e281fb9e92d9dd5bdfa1cf4eb6df2637c1a60303fbe48f` | recorded |
| Container | `aios-intelligence-ollama-staging` | `PASS` |
| Health | `GET /api/version` returned `{"version":"0.32.13"}` | `PASS` |

## Exact model identity

| Field | Verified value | Result |
|---|---|---|
| Model | `qwen2.5:1.5b-instruct-q4_K_M` | `PASS` |
| Manifest SHA-256 | `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` | `PASS` |
| Primary blob SHA-256 | `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` | `PASS` |
| Primary blob size | `986,048,512 bytes` | `PASS` |
| Quantization | `Q4_K_M` | `PASS` |

Checksums were recomputed read-only against the persisted manifest and blob.
The accepted provenance disposition remains `PASS WITH LIMITATION`.

Required limitation, carried forward verbatim:

`Canonical model family/repository verified; exact source revision of the Ollama conversion not independently attested.`

## Loaded and execution state

`GET /api/ps` returned `{"models":[]}`. Runtime logs contain acquisition and
read-only health/list operations only: `HEAD /`, `GET /api/version`,
`GET /api/ps`, `GET /api/tags`, and `POST /api/pull`. They contain no generate,
chat, embeddings, or runner-load request. Therefore:

- model present: `YES`;
- model loaded: `NO`;
- inference executed: `NO`;
- benchmark executed: `NO`.

## Storage and enforced ceilings

`/dev/loop0` reports `33,554,432` 512-byte sectors and is backed by
`/opt/aios/runtime/intelligence/staging/ollama/staging-root.ext4`, establishing
the exact `17,179,869,184-byte` (`16 GiB`) device ceiling. The mounted ext4
filesystem reported approximately `5.6 GiB` used and `10.0 GiB` filesystem
available (`~36%` used; operational capture approximately `10.7 GB` available).

Container inspection verified:

| Control | Enforced value | Result |
|---|---|---|
| Memory | `3,221,225,472 bytes` (`3 GiB`) | `PASS` |
| Memory swap | `3,221,225,472 bytes` (`3 GiB`) | `PASS` |
| CPU | `NanoCpus=1,000,000,000` (`1 vCPU`) | `PASS` |
| Active inference | `OLLAMA_NUM_PARALLEL=1` | `PASS` |
| Pending queue | `OLLAMA_MAX_QUEUE=1` | `PASS` |
| Loaded-model ceiling | `OLLAMA_MAX_LOADED_MODELS=1` | `PASS` |
| Keep-alive | `OLLAMA_KEEP_ALIVE=5m` | `PASS` |

The verification observed approximately `217.5 MiB / 3 GiB` runtime memory and
did not create load.
