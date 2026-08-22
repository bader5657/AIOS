# Test, Regression, Rollback, and Deferred Debt

## Focused tests

`tests/unit/brain/test_inference.py` must define its fake provider locally. The
fake implements `InferenceProvider`, exposes a valid `ProviderDescriptor`,
records received requests, and returns a supplied `InferenceResult` or raises a
controlled exception/cancellation. It uses no `httpx`, Ollama, network, or third
helper file.

Focused tests must prove:

- abstract-provider construction and async invocation;
- exact current schema version and fixed `STRUCTURED_INFERENCE` capability;
- exact `{instruction, data}` payload and preservation of IDs, timeout, schema
  reference, input reference, and context references;
- one provider call and the exact constructed request passed to it;
- successful and failed results returned by identity;
- unchanged propagation of every existing `FailureCode` result;
- no retry, fallback, or second call;
- construction errors, unexpected provider exceptions, and cancellation
  propagation; and
- no content logging, persistence, Memory, Specialists, business action, Core
  reverse dependency, concrete Ollama dependency, or hidden composition.

Durable AST/import/source audits must enforce the prohibited dependencies and
closed-world path set.

## Required regression matrix

After implementation, run focused invoker tests; Stage 0.3 contract tests;
Stage 0.5 provider abstraction tests; Stage 0.7 adapter tests; Core and relevant
Domain regressions; Stage 8 and Stage 9 gates; compile/static checks;
dependency/import and prohibited-source audits; `git diff --check`; and exact
closed-world path audit. No live staging inference is part of verification.

## Rollback

Rollback is repository-only removal/reversion of exactly the two authorized
implementation paths. No database, runtime, VPS, model, container, network, or
production rollback applies.

## Deferred Core handoff debt

The Core-to-Brain semantic receiver/input contract remains unresolved.
`CoreRouteResult` and `EventEnvelope` are not consumed by this implementation.
This does not block the repository-only invoker because it accepts explicit
Brain-local invocation arguments. No Core handoff is solved or authorized.

## Deferred composition and live-test debt

The concrete outer location for provider/config/schema assembly remains
unresolved. No composition root is created. A future live path—
`BrainInferenceInvoker → injected OllamaInferenceProvider → isolated staging
Ollama/Qwen → InferenceResult`—requires separate authority and synthetic data
only.

`/opt/aios/runtime/intelligence/staging/stage-0.8-src` remains preserved pending
separate cleanup authority and is not Brain source authority.
