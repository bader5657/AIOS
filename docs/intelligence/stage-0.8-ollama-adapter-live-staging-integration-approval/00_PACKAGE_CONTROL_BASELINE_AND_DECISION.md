# AIOS Intelligence Stage 0.8 — Package Control, Baseline, and Decision

## Package identity

- Stage: Intelligence Stage 0.8
- Purpose: Ollama adapter live staging integration evaluation and approval
- Classification: governance and controlled-execution approval only
- Assessment date: 2026-08-22 (Asia/Jakarta)
- Assessment baseline: `208c9f88832afcb9fd1bb2fa716ce30ef15653f7`
- Baseline state: `HEAD == main == origin/main`; worktree clean

## Accepted authority

- Intelligence Stage 0.6.4: BENCHMARK PASS WITH LIMITATION — VERIFIED — ACCEPTED — CLOSED
- Intelligence Stage 0.7 Input Payload Contract: VERIFIED — ACCEPTED — CLOSED
- Intelligence Stage 0.7 Ollama Adapter: VERIFIED — ACCEPTED — CLOSED
- Adapter implementation PR: #138
- Adapter implementation merge: `c64ae6d9364e175351aa7139f8da052d38056598`
- Runtime: Ollama 0.32.13
- Model: `qwen2.5:1.5b-instruct-q4_K_M`
- Runtime location: isolated staging at `http://172.31.63.2:11434`

## Decision

Exactly one synthetic live staging request is approved for controlled operator execution after this governance package becomes active. The request may exercise only:

`InferenceRequest -> OllamaInferenceProvider -> isolated staging Ollama/Qwen -> validated InferenceResult`

The accepted Stage 0.7 implementation must be used unchanged. This approval does not authorize adapter, contract, Core, provider-abstraction, Brain-orchestration, dependency, model, runtime, container, firewall, or production changes.

No inference was executed while preparing or approving this package.

## Decision boundary

A successful execution proves only adapter-to-staging-runtime interoperability. It does not prove Brain orchestration, production readiness, business-workflow correctness, Memory behavior, Specialist behavior, production inference safety, or production-scale capacity.
