# Test, Regression, Dependency, and Production Gates

## Focused test strategy

`tests/unit/brain/test_receiver.py` may define a recording
`BrainInferenceInvoker` subclass locally. It may return a controlled result or
raise a controlled exception/cancellation. No third helper path, provider,
Ollama, HTTP client, network, or live runtime is used.

Focused tests must prove:

- receiver construction, invoker validation, exact async one-input signature,
  and wrong-input fail-before-call behavior;
- exact intent-policy selection, instruction, `120000` timeout, and schema ref;
- absence of public override parameters and direct ID/data/reference values;
- exactly one invoker call and exact keyword argument set;
- successful and every failed result returned by identity;
- missing-policy `ValueError` before invocation;
- unexpected exception and cancellation propagation;
- no retry, fallback, second call, result rewrite, or failure-code fabrication;
  and
- no logging, persistence, Memory, Specialist, business/Domain, Core,
  concrete-provider/runtime, schema resolution, composition, or service wiring.

Durable AST/import/source audits must enforce the two-path closed world and all
prohibited dependencies. The receiver may import Brain input/inference
contracts and `BrainInferenceInvoker`, plus standard-library policy primitives;
it must not import `InferenceProvider` or concrete provider/runtime code.

## Regression matrix

After implementation run focused receiver tests, Stage 0.11 BrainInput tests,
Stage 0.9 invoker tests, Stage 0.7 mocked adapter tests, Stage 0.3 inference
contracts, Core and Domain regressions, Stage 8 and applicable Stage 9 gates,
full repository tests, compile/static, dependency/import and prohibited-source
audits, `git diff --check`, and exact two-path diff audit. No inference is part
of verification.

## Production and state boundaries

Logging, persistence, Memory, Specialist routing, business actions, Core
imports/wiring, provider configuration, retry, fallback, mapper behavior,
startup/service registration, production composition, and production
inference are all absent.
