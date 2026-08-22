# Controlled Measurement Evidence

| Field | Result |
|---|---|
| Runtime | Ollama `0.32.13` |
| Platform | `linux/amd64` |
| Image digest | `sha256:268c47cdc4718ded54babcd842579a7295ad79fd8d5c2ea64d7ba2e76872de6b` |
| Candidate model | Qwen2.5 1.5B Instruct `Q4_K_M`, approximately `986 MB` |
| Disposable filesystem | isolated `6 GiB` filesystem |
| Production Docker store used | `NO` |

The exact pinned Ollama image acquisition failed while extracting its large
image layer with `no space left on device`. No model was downloaded, no
inference was executed, and no container process was executed. Production
AIOS, PostgreSQL, and Telegram remained unaffected. Cleanup completed
successfully.

The verified classification is:

`DISK CEILING CONFLICT — PROJECT OWNER DECISION REQUIRED`

The prior `6 GiB` (`6,442,450,944 bytes`) ceiling was directly proven
insufficient. This evidence establishes a disk-ceiling conflict only. It does
not establish CPU, RAM, inference-quality, isolation, or production
suitability.
