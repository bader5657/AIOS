# Eligibility Order, Authority, and Independent Counters

## Frozen request path

1. Accept the exact raw candidate transiently from the operator-confirmed
   authority.
2. Invoke
   `evaluate_real_data_eligibility({"text": raw_text}, explicitly_authorized=True)`
   exactly once.
3. Allow the Stage 0.22 evaluator to own and invoke the internal Stage 0.17
   projection exactly once. The harness must not call
   `project_text_semantics` externally.
4. Inspect the returned `EligibilityResult`.
5. If `allowed == False`, stop before mapper and record
   `DENIED_BEFORE_BRAIN`.
6. Only if allowed, pass only `EligibilityResult.minimized_data` to
   `CoreToBrainMapper`, then `BrainInput`, existing Session-Bound Level B, and
   the provider.

Only the controlled future harness may set `explicitly_authorized=True`, and
only after it verifies this package, the exact candidate, and this exact
separately authorized session. Authorization is out-of-band and is not inferred
from candidate semantics.

## Allowed-path counters

| Counter | Required value |
|---|---:|
| `projector_call_count` | 1 |
| `eligibility_call_count` | 1 |
| `mapper_call_count` | 1 |
| `brain_call_count` | 1 |
| `provider_call_count` | 1 |
| `api_chat_call_count` | 1 |
| `admitted_request_count` | 1 |
| `retry_count` | 0 |
| `fallback_count` | 0 |

## Denied-path counters

| Counter | Required value |
|---|---:|
| `projector_call_count` | 1 |
| `eligibility_call_count` | 1 |
| `mapper_call_count` | 0 |
| `brain_call_count` | 0 |
| `provider_call_count` | 0 |
| `api_chat_call_count` | 0 |
| `admitted_request_count` | 0 |
| `retry_count` | 0 |
| `fallback_count` | 0 |

An eligibility denial has no override. It closes normally as `CLOSED_DENIED`
when safety, accounting, cleanup, and journal finalization are valid. Safety,
accounting, cleanup, contract, or runtime failure closes as `FAILED_CLOSED`.
