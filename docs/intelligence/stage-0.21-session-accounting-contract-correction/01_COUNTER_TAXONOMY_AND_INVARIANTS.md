# Corrected Counter Taxonomy and Invariants

Future Level B session harness final accounting must use explicit,
dimension-specific authoritative fields.

## Lifecycle instance counters

- `composition_instance_count`
- `client_instance_count`
- `provider_instance_count`
- `invoker_instance_count`
- `receiver_instance_count`
- `mapper_instance_count`

These fields count constructed objects or lifecycles only.

## Invocation counters

- `projector_call_count`
- `mapper_call_count`
- `brain_call_count`
- `provider_call_count`
- `api_chat_call_count`

These fields count actual calls only.

## Admission and policy counters

- `admitted_request_count`
- `retry_count`
- `fallback_count`

`admitted_request_count` counts admitted Brain requests only. Retry and
fallback remain separately recorded and must not be folded into another
counter.

Ambiguous generic final-accounting keys such as `mapper`, `provider`, `brain`,
and `client` are prohibited where lifecycle and call semantics could be
confused. An instance counter must never contribute arithmetically to a call
counter. This package does not authorize a generalized metrics framework.

## Two-request contract

```json
{
  "composition_instance_count": 1,
  "client_instance_count": 1,
  "provider_instance_count": 1,
  "invoker_instance_count": 1,
  "receiver_instance_count": 1,
  "mapper_instance_count": 1,
  "projector_call_count": 2,
  "mapper_call_count": 2,
  "brain_call_count": 2,
  "provider_call_count": 2,
  "api_chat_call_count": 2,
  "admitted_request_count": 2,
  "retry_count": 0,
  "fallback_count": 0
}
```

## Frozen invariants

1. Lifecycle instance counters count objects or lifecycles only.
2. Invocation counters count actual calls only.
3. `admitted_request_count` counts admitted Brain requests only.
4. Instance counters never contribute arithmetically to call counters.
5. Each admitted request corresponds to exactly one mapper call.
6. Each admitted request corresponds to exactly one Brain call.
7. Each admitted request corresponds to exactly one provider inference.
8. Under the current no-retry/no-fallback policy, each admitted request
   corresponds to exactly one `/api/chat` call.
9. `retry_count` and `fallback_count` remain separately recorded.
10. Final accounting fails closed on any actual invariant mismatch.

Raw independent counters are authoritative. If they disagree, the session is
`FAILED_CLOSED`. If raw counters agree but a derived presentation field is
wrong, governance records an accounting defect without manufacturing extra
execution. Inference must not be rerun solely to repair presentation evidence.

