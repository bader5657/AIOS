# Chain, Identity, Data, and Dependency Evidence

The verified repository-only interoperability chain is:

`eligible CoreRouteResult → CoreToBrainMapper → BrainInput → BrainSemanticReceiver → BrainInferenceInvoker → fake InferenceProvider → InferenceResult`

The integration evidence proves one deterministic UUIDv4-derived request ID is
created only by the mapper, while the caller-owned correlation ID is preserved.
The mapper emits `BrainIntent.STRUCTURED_INFERENCE`, snapshots input data
immutably, and propagates the input and context provenance references.

The receiver applies its exact static policy and constructs the exact
`InferenceRequest`. The fake provider is called exactly once. The returned
success object is preserved by identity, the representative `TIMEOUT` failure
object is preserved by identity without retry, and an ineligible Core route
fails before UUID generation or provider activity.

Dependency/import and prohibited-source audits pass. The narrow Stage 0.14
`core/core_to_brain_mapper.py → core.brain.input_contracts` exception remains
exactly preserved, with no broader Core-to-Brain import. The test-local provider
attribute remains `received`, not `requests`.

This evidence proves repository composability only. It creates no production
code, runtime wiring, provider network call, model load, schema binding,
production composition, Memory or Specialist behavior, business behavior, or
production activation.
