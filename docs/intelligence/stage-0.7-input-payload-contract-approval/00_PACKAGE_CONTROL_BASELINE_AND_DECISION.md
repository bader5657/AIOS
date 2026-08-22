# AIOS Intelligence Stage 0.7 — Input Payload Contract Evaluation and Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / CONTRACT APPROVAL ONLY` |
| Assessment baseline | `1abba49f923559c3969444bb81e614b335f6ad67` |
| Baseline state | `HEAD == main == origin/main`; tracked worktree clean |
| Stage 0.6.4 | `BENCHMARK PASS WITH LIMITATION — VERIFIED — ACCEPTED — CLOSED` |
| Stage 0.7 adapter boundary | `IDENTIFIED` |
| Prior adapter approval | `BLOCKED — INPUT PAYLOAD CONTRACT REQUIRED` |
| Payload decision | `VERIFIED — ACCEPTED — CLOSED` |
| Architecture change required | `NO` |
| Adapter/Brain/production authority | `NONE` |

## Decision

The first structured-inference path uses one minimal provider-neutral semantic
profile inside the existing `InferenceRequest.input_payload` field:

```json
{
  "instruction": "<string>",
  "data": {}
}
```

This freezes payload semantics without changing the `InferenceRequest` field
list, wire representation, canonical architecture, provider abstraction, or
Core boundary. It describes AIOS inference intent and data, not an Ollama or
other provider request.

No adapter, validator, Brain flow, source/test/configuration, inference,
runtime mutation, or production integration is created or authorized here.

## Preserved benchmark limitation

`The first official cold structured-output request produced a contained schema-invalid confidence value (100 instead of 0.0–1.0). The result was rejected correctly. After methodology clarification, all 20 official warm requests were valid. Official reliability is therefore 20/21 (95.24%).`

The limitation remains unchanged.
