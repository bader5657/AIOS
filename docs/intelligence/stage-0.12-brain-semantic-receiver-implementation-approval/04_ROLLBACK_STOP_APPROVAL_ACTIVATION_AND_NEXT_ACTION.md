# Rollback, Stop Conditions, Approval, Activation, and Next Action

## Rollback

Rollback is repository-only removal or reversion of exactly:

- `core/brain/receiver.py`; and
- `tests/unit/brain/test_receiver.py`.

No VPS, database, runtime, service, model, container, network, or temporary
source rollback applies.

## Stop conditions

Stop and return to governance if implementation requires a third path,
`BrainInput` or `BrainInferenceInvoker` change, Core change, schema
registry/resolver/validator module, provider/runtime dependency, mapper,
composition root, Memory/Specialist/business logic, new dependency, live
inference, or runtime mutation. A third path is `SCOPE EXPANSION REQUIRED`; an
authority/invariant conflict is `BLOCKED`.

## Deferred boundaries

The mapper remains unimplemented. Resolver/validator binding and production
composition remain unresolved. A live synthetic receiver chain requires
separate future authority. Preserve Stage 0.8 and Stage 0.10 temporary staging
sources; cleanup remains separately governed.

## Project Owner approval

I, as Project Owner, authorize repository-only implementation of the Stage
0.12 BrainSemanticReceiver and its exact static STRUCTURED_INFERENCE policy.

The receiver may consume one immutable BrainInput, derive only the approved
Brain-owned instruction, timeout, and output schema reference, invoke the
unchanged BrainInferenceInvoker exactly once using IDs and references directly
from BrainInput, and return the exact InferenceResult unchanged.

No Core wiring, mapper implementation, schema resolver/validator binding,
provider/runtime dependency, Memory, Specialist routing, business action,
retry, fallback, persistence, live inference, production composition, or
production activation is authorized.

## Publication, activation, and next action

The allowed governance diff is this package only. After normal clean merge and
a synchronized clean-main audit, authority activates as:

`INTELLIGENCE STAGE 0.12 BRAIN SEMANTIC RECEIVER IMPLEMENTATION APPROVED — READY TO BUILD`

The exact next action is repository-only implementation and verification of
the two authorized paths. Activation itself changes no implementation or
runtime and executes no inference.
