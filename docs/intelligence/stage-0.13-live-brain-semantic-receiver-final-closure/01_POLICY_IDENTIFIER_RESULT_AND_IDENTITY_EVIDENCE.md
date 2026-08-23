# Policy, Identifier, Result, and Identity Evidence

## Static receiver policy

The receiver applied exactly:

- intent: `BrainIntent.STRUCTURED_INFERENCE`;
- instruction: `Analyze the provided data and return one concise result string in the required structured output.`;
- timeout: `120000` ms; and
- output schema reference: `brain_structured_inference_result_v1`.

## Identifier control

| Identifier | Approved | Executed/result |
|---|---|---|
| Correlation ID | `stage-0.13-live-1` | `stage-0.13-live-1` |
| Request ID | `stage-0.13-live-request-1` | `stage-0.13-live-request-1` |

The harness compared the approved and executable constants for exact equality
before inference. The equality gate passed with no identifier variance. Both
identifiers originated in the single `BrainInput` and were preserved through
the returned result.

## Result evidence

| Field | Value |
|---|---|
| `success` | `True` |
| `failure_code` | `None` |
| `provider_id` | `ollama-local` |
| `model_id` | `qwen2.5:1.5b-instruct-q4_K_M` |
| `duration_ms` | `49785` |
| Independent structured validation | `PASS` |
| Result identity | `PASS — exact provider result preserved` |

The structured output independently satisfied the exact one-member object
schema whose required `result` member is a string and which permits no
additional properties. The provider-neutral `InferenceResult` passed through
the invoker and receiver without wrapper, rewrite, normalization, repair, raw
response substitution, or Brain-local business interpretation.
