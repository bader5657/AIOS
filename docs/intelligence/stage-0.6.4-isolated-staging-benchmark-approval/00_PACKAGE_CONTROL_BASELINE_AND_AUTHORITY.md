# AIOS Intelligence Stage 0.6.4 — Isolated Staging Benchmark Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / BENCHMARK APPROVAL ONLY` |
| Approval baseline | `378b432fd87ef05450eec5f24dc2490112157df0` |
| Baseline state | `HEAD == main == origin/main`; tracked worktree clean |
| Stage 0.6.3 | `ISOLATED STAGING INSTALLATION VERIFIED — ACCEPTED — CLOSED` |
| Runtime | Ollama `0.32.13` |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| Container | `aios-intelligence-ollama-staging` |
| Network | internal `aios-ollama-runtime`; no public exposure |
| Approval disposition | `BENCHMARK APPROVED — READY FOR CONTROLLED EXECUTION` |
| Production authority | `NONE` |

This package defines and approves the first bounded execution of the installed
model. It does not execute inference, load the model, benchmark the runtime,
integrate a provider, change production, or grant production authority.

The controlled execution may use synthetic inputs only and must remain within
the existing `16 GiB` staging disk, `3 GiB` RAM, `1 vCPU`, concurrency `1`,
queue `1`, and `120000 ms` maximum timeout. Retry, fallback, and dynamic routing
remain `NONE`.

Package:

- `01_BENCHMARK_REQUEST_SCHEMA_AND_SAMPLING.md`;
- `02_METRICS_MONITORING_AND_MEASUREMENT.md`;
- `03_FAILURE_TIMEOUT_MALFORMED_AND_STOP_CONTROLS.md`;
- `04_ACCEPTANCE_CLASSIFICATION_AND_STAGE_BOUNDARY.md`;
- `05_PROJECT_OWNER_APPROVAL_PUBLICATION_AND_ACTIVATION.md`.

`INTELLIGENCE STAGE 0.6.4 BENCHMARK APPROVED — READY FOR CONTROLLED EXECUTION`
