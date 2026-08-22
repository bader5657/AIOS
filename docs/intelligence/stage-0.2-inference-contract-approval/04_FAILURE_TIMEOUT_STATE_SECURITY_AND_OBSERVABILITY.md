# Failure, Timeout, State, Security, and Observability

## Initial failure taxonomy

The complete initial enum is exactly:

```python
class InferenceFailureCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    TIMEOUT = "timeout"
    PROVIDER_FAILURE = "provider_failure"
    MALFORMED_OUTPUT = "malformed_output"
    POLICY_DENIED = "policy_denied"
    RESOURCE_LIMIT = "resource_limit"
```

No additional code is authorized by this package. Provider-unavailable and
local-runtime details map to the smallest applicable approved code rather than
expanding the taxonomy without evidence.

Partial or malformed provider output is fail-closed:

- `success=False`;
- `failure_code=MALFORMED_OUTPUT`;
- `structured_output=None`; and
- raw/partial content is discarded.

There is no partial-success state in v1.

## Timeout and retry

Brain supplies `timeout_ms` from approved configuration and owns the invocation
ceiling. The inference/provider runtime enforces it, may use a shorter internal
timeout, and may not extend it. Expiry returns `TIMEOUT` with no automatic
retry. `INTELLIGENCE RETRY = NONE BY DEFAULT` remains binding.

## State, Memory, Specialist, tool, and business boundaries

- request, result, raw prompt/response, embedding, token data, and session
  context: no automatic persistence;
- transient data: one invocation only;
- context references: no cross-request Memory, retrieval, embedding store,
  session store, or Memory API;
- result destination: Brain orchestration only;
- direct inference-to-Specialist invocation: prohibited;
- tools/functions/tool-call fields and execution: prohibited;
- customer/order/product/HPP/inventory/transaction/report/workflow completion
  fields or semantics: prohibited.

## Security and policy boundary

The initial DTOs do not embed a broad trust/data-classification policy model.
Brain applies separately approved policy before request construction.
`POLICY_DENIED` represents fail-closed refusal, including before provider
execution. Policy references, trust models, and data-classification vocabulary
require separate authority.

## Observability and privacy

Only bounded metadata is loggable by default:

- `correlation_id`;
- `request_id`;
- `provider_id`;
- `model_id`;
- `duration_ms`;
- `success`; and
- `failure_code`.

`input_payload`, `structured_output`, prompts, raw responses, Telegram content,
user/business content, failure content containing such data, and credentials
must not be logged by default. Stage 9 journald privacy findings remain active.

Provider/model identifiers expose no endpoint, account, credential, or secret
reference. Token and cost metadata remain deferred because paid-provider
authority does not exist and the initial local-first contract stays minimal.
