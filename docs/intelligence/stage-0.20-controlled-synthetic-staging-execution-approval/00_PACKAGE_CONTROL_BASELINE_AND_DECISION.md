# Intelligence Stage 0.20 — Controlled Synthetic Staging Execution Approval

| Control | Approved value |
|---|---|
| Work type | `FORMAL EXECUTION APPROVAL` |
| Approval baseline | `d20176a60fa75cbe7de015343772254127860f35` |
| Stage 0.19 | `VERIFIED — ACCEPTED — CLOSED` |
| Architecture change | `NO` |
| Requests | exactly `1` synthetic staging inference |
| Level B / production | `NOT AUTHORIZED / PROHIBITED` |
| Decision | `APPROVED AFTER GOVERNANCE ACTIVATION` |

This package authorizes exactly one post-route synthetic staging request after
an immediately passing operational preflight. It does not authorize Universal
Ingestion, real Core routing, Telegram or business data, repeated use,
benchmarking, retry, fallback, production integration, or persistent Level B
activation.

The execution must use the repository projector, CoreToBrainMapper, Stage 0.19
composition, Stage 0.18 schema binding, receiver, invoker, provider, and the
already-isolated Ollama/Qwen runtime. No repository source change is part of
the execution.
