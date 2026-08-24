# Ordering, Authority, Admission, and Accounting

## Frozen execution order

1. Verify active session-specific real-text authority and explicit operator
   opt-in.
2. Accept the one confirmed raw plain-text candidate transiently in memory.
3. Call `evaluate_real_data_eligibility({"text": raw_text},
   explicitly_authorized=True)` exactly once.
4. The Stage 0.22 evaluator invokes the governed Stage 0.17 projection exactly
   once internally.
5. If denied, stop before mapper and close under the denial contract.
6. If allowed, use only `EligibilityResult.minimized_data` and verify its exact
   `{"text": normalized_text}` shape.
7. Increment `admitted_request_count` from zero to one immediately before
   mapper/Brain continuation.
8. Invoke `CoreToBrainMapper`; the mapper alone creates the Brain request ID.
9. Traverse `BrainInput`, the existing Session-Bound Level B Brain boundary,
   provider, and schema validation.
10. Display the result to the operator without persisting raw output.

The harness must not call `project_text_semantics` externally. External
projection would duplicate the evaluator-owned projection and violate exact
accounting.

Only the controlled harness may supply the trusted out-of-band authorization
flag, after it verifies execution authority, operator opt-in, and the confirmed
candidate. Authorization is never inferred from semantic content.

A correlation ID may be created for session evidence before eligibility. A
denied request has no Brain request ID because the mapper is not called.

## Exact counters

For one allowed request:

| Counter | Value |
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

For eligibility denial:

| Counter | Value |
|---|---:|
| `projector_call_count` | 1 |
| `eligibility_call_count` | 1 |
| `mapper_call_count` | 0 |
| `brain_call_count` | 0 |
| `provider_call_count` | 0 |
| `api_chat_call_count` | 0 |
| `admitted_request_count` | 0 |

No second request, retry, fallback, alternate candidate, or second session is
permitted under the first-session authority.

Normal DLP denial is classified `DENIED_BEFORE_BRAIN` and finalizes as
`CLOSED_DENIED` if accounting, cleanup, and safety remain correct.
`FAILED_CLOSED` is reserved for accounting, cleanup, safety, contract, or
runtime failure.
