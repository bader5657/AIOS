# Dependency, Privacy, Test, and Deferred Boundaries

## Dependency and production boundary

`receiver.py` may import only `BrainInput`, `BrainIntent`,
`BrainInferenceInvoker`, and standard-library policy primitives. It imports no
result contract merely for annotation, Core, `EventEnvelope`,
`CoreRouteResult`, concrete provider, Ollama, HTTP/runtime/network,
configuration, Memory, Specialist, or business module.

The first implementation is repository/test-only. It creates no singleton,
startup registration, service wiring, production composition, or inference
activation. There is no logging or persistence.

## Proposed future paths

Exactly two paths are sufficient:

1. `core/brain/receiver.py`
2. `tests/unit/brain/test_receiver.py`

The static policy remains private in `receiver.py`; no third policy module is
justified.

## Future unit-test strategy

Tests must use a recording `BrainInferenceInvoker` subclass or real invoker
with a fake provider and prove exact constructor/input types, policy selection,
instruction/timeout/schema values, direct ID/data/reference propagation, one
invoker call, exact argument set, result identity for success and every failed
result, unsupported policy fail-before-call, exception/cancellation
propagation, and absence of retry/fallback.

Static/source tests must prove no content logging, persistence, Memory,
Specialist, business action, Core/concrete-provider/runtime import, schema
resolution, composition root, or extra path.

## Deferred boundaries

The Core-to-Brain mapper remains unimplemented; the receiver accepts only
`BrainInput`. Production/outer composition and resolver binding remain
unresolved. A later separately approved synthetic live chain may evaluate:

`BrainInput → BrainSemanticReceiver → BrainInferenceInvoker → injected OllamaInferenceProvider → isolated Qwen → InferenceResult`

No live inference is authorized here. Preserve the Stage 0.8 and Stage 0.10
temporary staging sources; cleanup remains separately governed.
