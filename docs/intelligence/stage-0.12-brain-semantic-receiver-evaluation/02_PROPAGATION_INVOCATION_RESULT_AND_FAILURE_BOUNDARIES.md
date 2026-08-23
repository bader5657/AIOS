# Propagation, Invocation, Result, and Failure Boundaries

## Exact propagation

The receiver passes directly from `BrainInput`:

- `correlation_id`;
- `request_id`;
- `data`;
- `input_reference`; and
- `context_references`.

It does not copy IDs into policy constants or accept duplicate ID arguments.
Structural direct access eliminates the Stage 0.10 mismatch class. Data remains
semantically unchanged and immutable; no enrichment, retrieval, conversion,
or business-object handling occurs. References remain opaque and are not
dereferenced.

## Invocation and result

The receiver calls `await invoker.invoke(...)` exactly once. There is no
health call, retry, fallback, loop, second request, or alternate policy. It
returns the exact `InferenceResult` object unchanged, including every failed
result. It creates no receiver DTO and makes no business-success claim.

## Failure behavior

- wrong receiver input type raises `TypeError` before invocation;
- missing/unsupported intent policy raises `ValueError` before invocation;
- the private static policy is construction-time governance and is not mutable
  or caller-configurable;
- failed `InferenceResult` passes through unchanged;
- unexpected invoker/provider exceptions propagate unchanged; and
- cancellation propagates unchanged.

No new exception hierarchy and no provider `FailureCode` are used for
pre-inference receiver/policy failures. Every receiver-local failure causes
zero invoker/provider calls.
