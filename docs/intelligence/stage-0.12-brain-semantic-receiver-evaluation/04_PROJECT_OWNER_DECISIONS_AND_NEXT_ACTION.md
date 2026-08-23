# Project Owner Decisions and Next Action

## Decisions requiring ratification

The implementation approval must explicitly ratify:

1. `BrainSemanticReceiver` and `core/brain/receiver.py`;
2. constructor injection of exactly one `BrainInferenceInvoker`;
3. private immutable module-local policy mapping;
4. the exact static instruction;
5. timeout `120000` ms;
6. `brain_structured_inference_result_v1` and its exact one-field bounded
   schema semantics;
7. direct ID/data/reference derivation from `BrainInput`;
8. `TypeError`/`ValueError` pre-inference semantics; and
9. exactly two future implementation paths.

There is no architecture-change blocker. Resolver binding is required before a
future live request but does not block repository-only receiver implementation
and unit verification.

## Recommended next action

Create:

`Intelligence Stage 0.12 — Brain Semantic Receiver Implementation Approval`

That governance package must freeze the exact class/method signature, policy
record, allowed imports, two-path closed world, focused tests, regression
matrix, rollback, and stop conditions. It must not authorize a mapper, Core
wiring, composition root, live inference, or runtime mutation.

Evaluation disposition:

`INTELLIGENCE STAGE 0.12 BRAIN SEMANTIC RECEIVER BOUNDARY IDENTIFIED — READY FOR GOVERNANCE APPROVAL`
