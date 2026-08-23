# Fake Provider, Request, Result, and Failure Cases

## Test-local provider seam

Define the fake inside the sole test file as an `InferenceProvider` with a valid
`ProviderDescriptor`, `ProviderRuntimeKind.LOCAL`, and exactly
STRUCTURED_INFERENCE capability. It records received InferenceRequest objects,
counts calls, and returns one configured prebuilt InferenceResult. It has no
network, concrete adapter, provider-specific logic, retry, or fallback.

The exact captured request must contain the accepted inference schema version,
BrainInput-derived IDs, STRUCTURED_INFERENCE capability, exact instruction and
immutable data payload, `120000` ms timeout, exact output-schema reference, and
unchanged opaque provenance.

## Success and identity

Use a valid successful result with `{"result": "normal"}`, provider ID
`stage-0.15-fake-provider`, model ID `stage-0.15-fake-model`, no failure code,
and bounded duration. Assert the integration return `is` the exact prebuilt
result from fake provider through real BrainInferenceInvoker and
BrainSemanticReceiver. The fake is called exactly once.

## Representative failure

Run a separate repository-only chain with one valid failed result using
`FailureCode.TIMEOUT`. Assert exact object identity returns unchanged, without
retry, exception conversion, wrapper, rewrite, or second call.

## Pre-Brain failure isolation

Use one ineligible CoreRouteResult and require `ValueError` before UUID factory
consumption, BrainInput downstream use, receiver call, invoker execution, or
provider call. Recording counters must remain zero.

Across cases, correlation ID originates only with the caller and request ID
only with the mapper. Receiver and invoker consume BrainInput-derived values.
