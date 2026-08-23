# Exact Invocation, Static Policy, and PASS Criteria

The harness must call exactly once:

`await receiver.receive(brain_input)`

It must not directly call `invoker.invoke(...)` or `provider.infer(...)`.
Recording overrides may call their respective `super()` implementation exactly
once only as transparent instrumentation.

The recorded invoker arguments must prove the receiver selected exactly:

- instruction: `Analyze the provided data and return one concise result string in the required structured output.`;
- timeout: `120000` ms; and
- output schema reference: `brain_structured_inference_result_v1`.

They must also prove correlation/request IDs, immutable data,
`input_reference`, and `context_references` came unchanged from the single
`BrainInput`.

## PASS criteria

PASS requires all of:

- valid exact `BrainInput` and receiver as the actual live entrypoint;
- exact static policy and direct identifier/reference/data propagation;
- receiver, invoker, provider, and live HTTP request counts each exactly one;
- no direct harness bypass, retry, fallback, second request, or health request;
- `success is True` and `failure_code is None`;
- `provider_id == "ollama-local"`;
- `model_id == "qwen2.5:1.5b-instruct-q4_K_M"`;
- exact approved correlation and request IDs in the result;
- `structured_output` is exactly one mapping member named `result`, containing
  a string, and independently validates;
- duration is valid and bounded;
- the exact provider result identity passes through invoker and receiver to the
  caller without wrapper, rewrite, normalization, or business interpretation;
- no raw provider response exposure; and
- mandatory preflight and postflight pass.

A failed `InferenceResult` is preserved with its exact `FailureCode` and is not
retried. Unexpected exceptions/cancellation propagate and are recorded for
governance without retry. Success must never be manufactured.
