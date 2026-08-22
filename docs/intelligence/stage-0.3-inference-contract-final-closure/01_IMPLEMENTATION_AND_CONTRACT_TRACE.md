# Implementation and Contract Trace

## PR and closed-world path trace

Implementation commit `7f00166e12fa63a8ce082f240547046db5fb346f`
was normal-merged by PR #115 as merge commit
`16a0184519e2d3f77d373d92928385632438da44`.

The PR introduced exactly three authorized paths:

1. `core/brain/__init__.py`
2. `core/brain/inference_contracts.py`
3. `tests/unit/brain/test_inference_contracts.py`

No other implementation path changed. Recorded merge-baseline blobs:

| Path | Blob |
|---|---|
| `core/brain/__init__.py` | `f254074d7720e9aeba5e8c90d6cb4af1b306e59c` |
| `core/brain/inference_contracts.py` | `931cb3e917a5515f462f9a1d7250ebc6e83ba77a` |
| `tests/unit/brain/test_inference_contracts.py` | `6f733ddb9d2a2704f06bcbe5e782e21d9b2331b0` |

The initializer is minimal and has no import, export, or side effect that
activates a Brain runtime.

## Exact implemented symbols

- `InferenceCapability`: `str, Enum`, sole member
  `STRUCTURED_INFERENCE = "structured_inference"`;
- `FailureCode`: `str, Enum`, exactly
  `INVALID_REQUEST`, `RUNTIME_UNAVAILABLE`, `TIMEOUT`, `PROVIDER_FAILURE`,
  `MALFORMED_OUTPUT`, `POLICY_DENIED`, and `RESOURCE_LIMIT`, with their
  approved lowercase stable values;
- `InferenceRequest`: frozen and slotted Brain-owned request dataclass; and
- `InferenceResult`: frozen and slotted Brain-owned result dataclass.

Both contracts are runtime-local, non-canonical, provider-neutral, stateless
per invocation, and subordinate to future separately approved Brain behavior.

## Field trace

`InferenceRequest` declares exactly the required fields `schema_version`,
`correlation_id`, `request_id`, `capability`, `input_payload`, `timeout_ms`, and
`output_schema_ref`, plus optional `input_reference` and
`context_references`.

`InferenceResult` declares exactly `schema_version`, `correlation_id`,
`request_id`, `success`, `failure_code`, `structured_output`, `provider_id`,
`model_id`, and `duration_ms`, plus optional `failure_detail` and `warnings`.

Provider/model configuration, deadline, raw response, token/cost metadata,
tools, session, persistence, Memory, Specialist, and business action/completion
fields are absent.
