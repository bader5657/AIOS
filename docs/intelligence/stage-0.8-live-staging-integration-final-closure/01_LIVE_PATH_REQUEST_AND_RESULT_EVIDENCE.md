# Live Path, Request, and Result Evidence

## Isolated live path

The successful supplied path was:

`InferenceRequest → OllamaInferenceProvider → isolated Ollama 0.32.13 → Qwen2.5 1.5B Instruct Q4_K_M → provider response → JSON parsing → independent schema validation → InferenceResult`

Import-isolation preflight passed. Adapter and inference contracts were imported
from the temporary Stage 0.8 checkout at accepted source SHA
`d0c8a317e097624f771dc016dcc3f618afc73f70`, not from production source.
Production source remained at
`2c44dc84cb38dc51778f8a65f12a6e59683c74c9` and was not updated, checked out,
pulled, reset, deployed, or otherwise mutated.

## Request and validation contract

- data class: synthetic only; no Telegram, customer, order, business, secret, or
  production content
- input payload: accepted Stage 0.7 provider-neutral object with `instruction`
  and `data`
- output schema: bounded synthetic sensor classification with `category` equal
  to `normal` or `warning`, and numeric `confidence` in `0.0–1.0`
- schema resolver: temporary bounded operator-side resolver
- validator: temporary independent operator-side validator
- repository harness: none added

## Accepted result evidence

The supplied execution evidence confirms:

- `result.success = True`
- `failure_code = None`
- `provider_id = ollama-local`
- `model_id = qwen2.5:1.5b-instruct-q4_K_M`
- correlation ID and request ID were preserved
- structured output passed independent validation
- `duration_ms` satisfied the accepted result contract
- no raw provider response was exposed
- no retry occurred
- exactly one adapter invocation occurred

No unrecorded duration, identifier value, structured-output content, provider
content, or raw response is asserted by this closure.
