# Dependency, Test, Rollback, and Stop Contract

## Dependency and side-effect boundary

The single test may import verified Core route contracts, CoreToBrainMapper,
BrainInput/BrainIntent, BrainSemanticReceiver, BrainInferenceInvoker,
InferenceProvider and descriptor/runtime types, InferenceRequest/Result,
FailureCode, and their existing constants. Use standard-library `asyncio.run`
and UUID/test helpers; no new dependency or pytest-asyncio is required.

OllamaInferenceProvider/config, httpx, network, database, Registry, Storage,
filesystem effects, EventEnvelope, RequestContext, Memory, Specialist, business
modules/actions, persistence, logging, and runtime lifecycle are prohibited.
Existing Stage 8/9 policies require no change. If a test-policy path becomes
necessary, stop for scope expansion.

## Verification matrix

Without live inference, run the Stage 0.15 integration test; focused mapper,
BrainInput, receiver, invoker, adapter, and inference-contract tests; Core and
Domain regressions; Stage 8 and Stage 9 gates; full repository suite;
compile/static, dependency/import, and prohibited-source audits;
`git diff --check`; and exact one-path closed-world audit. Zero unresolved
failures are required.

## Rollback and stop conditions

Rollback removes only `tests/integration/test_core_to_brain_chain.py`. No VPS,
runtime, database, or service rollback exists.

Stop if production code, a second test/policy path, a Core/Brain contract or
receiver/invoker change, new dependency, live inference, Ollama/httpx,
database/network, or production composition becomes necessary. Report the
exact incompatibility rather than patching production under this authority.

Test-local construction of fake provider, invoker, receiver, and mapper is not
a production composition root. Production schema binding is not required
because the fake returns a prebuilt validated InferenceResult.
