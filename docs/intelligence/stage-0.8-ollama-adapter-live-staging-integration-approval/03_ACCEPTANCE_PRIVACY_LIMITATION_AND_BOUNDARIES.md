# Acceptance, Privacy, Limitation, and Boundaries

## Success criteria

The controlled execution passes only if all of the following are evidenced:

- one and only one adapter `POST /api/chat` occurred;
- the runtime completed successfully;
- provider content parsed as one JSON object;
- the injected independent validator ran and passed;
- `InferenceResult.success is True` and `failure_code is None`;
- validated `structured_output` is present;
- `provider_id == "ollama-local"`;
- `model_id == "qwen2.5:1.5b-instruct-q4_K_M"`;
- the fixed correlation and request identifiers are preserved;
- `duration_ms` satisfies the accepted result contract;
- no raw provider response is exposed;
- no retry, fallback, or second request occurred;
- every preflight and postflight safety requirement passes.

Any missing criterion makes the execution non-passing and requires governance review. It does not authorize a repeat.

## Logging and privacy

Instruction, input data, structured output, provider message content, and raw provider response are content and must not be logged or printed. Only bounded metadata may be recorded: correlation ID, request ID, provider ID, model ID, duration, success/failure, failure code, request count, and safety observations.

The raw provider response remains transient and must not be returned outside the accepted `InferenceResult`, cached, persisted, or included in evidence.

## Preserved benchmark limitation

`The first official cold structured-output request produced a contained schema-invalid confidence value (100 instead of 0.0–1.0). The result was rejected correctly. After methodology clarification, all 20 official warm requests were valid. Official reliability is therefore 20/21 (95.24%).`

The Stage 0.8 validator must preserve the same fail-closed behavior: a value such as `100` is rejected, never coerced to `1.0`, repaired, retried, or hidden.

## Non-authority

This approval grants no production inference, production endpoint, Brain wiring, Core change, business use, automated decision, provider/model routing, retry, fallback, persistence, conversation/session state, new dependency, provider SDK, or runtime-lifecycle authority.
