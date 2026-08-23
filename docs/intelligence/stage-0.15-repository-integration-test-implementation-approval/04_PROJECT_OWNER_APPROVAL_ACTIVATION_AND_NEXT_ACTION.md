# Project Owner Approval, Activation, and Next Action

## Project Owner approval

I, as Project Owner, authorize repository-only implementation of one Stage
0.15 integration test proving the existing CoreToBrainMapper, BrainInput,
BrainSemanticReceiver, BrainInferenceInvoker, and fake InferenceProvider
compose correctly.

The test may use deterministic synthetic identifiers/data and a test-local fake
provider.

No production code change, live inference, Core runtime wiring, schema binding,
production composition, Memory, Specialist routing, business behavior, or
production activation is authorized.

## Publication and activation

The allowed diff for this approval is this governance package only.
Publication requires a normal clean, mergeable PR into `main`, without force or
history rewrite. After merge and synchronized clean-main audit, authority
activates as:

`INTELLIGENCE STAGE 0.15 REPOSITORY INTEGRATION TEST IMPLEMENTATION APPROVED — READY TO BUILD`

Activation creates no test, production code, integration runtime, wiring, or
inference.

## Deferred boundaries and next action

Core wiring, production schema binding, and production composition remain
unresolved and unauthorized. Passing and closing Stage 0.15 may make Stage 0.16
Core-to-Brain Runtime Wiring Boundary Evaluation eligible; it is not evaluated
or authorized here.

The exact next action is:

`Intelligence Stage 0.15 — implement exactly tests/integration/test_core_to_brain_chain.py, run the complete approved non-live verification matrix, and return evidence for final review.`
