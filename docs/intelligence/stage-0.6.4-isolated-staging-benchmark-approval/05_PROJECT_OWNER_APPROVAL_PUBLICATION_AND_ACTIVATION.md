# Project Owner Approval, Publication, and Activation

## Project Owner approval

I, as Project Owner, authorize a bounded isolated staging benchmark of the installed Ollama 0.32.13 + Qwen2.5 1.5B Instruct Q4_K_M runtime.

The benchmark may execute synthetic structured-inference requests only.

It must remain within 3 GiB RAM, 1 vCPU, concurrency 1, no public exposure, no production integration, and must stop immediately if AIOS, PostgreSQL, Telegram polling, host stability, or swap behavior degrades.

This approval does not authorize production inference or Brain integration.

## Publication and activation

Activation requires review and merge of this exact package from branch
`governance/intelligence-stage-0.6.4-benchmark-approval`. Before controlled
execution, the operator must confirm the merged commit, reverify Stage 0.6.3
runtime identity and isolation, and capture the complete Step 1 baseline.

The approval activates only the procedure, request count, synthetic payloads,
limits, monitoring, stop conditions, and classification gates recorded here.
It does not activate the model during this governance task.

## Remaining blockers and next action

There is no governance-design blocker to controlled execution after merge.
Execution remains blocked until the approval is merged and an operator begins
the exact monitored procedure. No benchmark result or feasibility
classification exists yet.

Next official action:

`Intelligence Stage 0.6.4 — execute the approved bounded isolated staging benchmark and return the evidence for acceptance classification.`

`INTELLIGENCE STAGE 0.6.4 BENCHMARK APPROVED — READY FOR CONTROLLED EXECUTION`
