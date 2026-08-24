# Stage 0.20 — Controlled Synthetic Execution Evidence Path Reconciliation

| Control | Authorized value |
|---|---|
| Work type | `GOVERNANCE / EVIDENCE-PATH AUTHORIZATION ONLY` |
| Authority baseline | `e8260954b1c0dce71643b9272ddef4ab31460580` |
| Previous result | `PREFLIGHT BLOCKED — NO INFERENCE EXECUTED` |
| Cumulative live inference count | `0` |
| Existing execution record | `00_CONTROLLED_SYNTHETIC_EXECUTION.json` — immutable historical blocked-attempt evidence |
| Privileged network record | `01_PRIVILEGED_NETWORK_PREFLIGHT.txt` — immutable approved evidence |
| New execution record | `02_CONTROLLED_SYNTHETIC_EXECUTION.json` |
| Inference in this task | `PROHIBITED` |
| Runtime/source mutation | `PROHIBITED` |
| Decision | `APPROVED AFTER GOVERNANCE ACTIVATION` |

This package reconciles only the immutable evidence target for the next
authorized Stage 0.20 attempt. It does not execute or broaden the controlled
synthetic inference authority. All request, identity, chain, runtime, safety,
and postflight controls in the existing Stage 0.20 approval remain unchanged.

The records at
`/opt/aios/runtime/intelligence/staging/stage-0.20-evidence/00_CONTROLLED_SYNTHETIC_EXECUTION.json`
and
`/opt/aios/runtime/intelligence/staging/stage-0.20-evidence/01_PRIVILEGED_NETWORK_PREFLIGHT.txt`
must remain unmodified. The next attempt may write only
`/opt/aios/runtime/intelligence/staging/stage-0.20-evidence/02_CONTROLLED_SYNTHETIC_EXECUTION.json`.
