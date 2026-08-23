# Rollback, Stop Conditions, Approval, Activation, and Next Action

## Rollback

Rollback is repository-only removal or reversion of exactly:

- `core/brain/input_contracts.py`; and
- `tests/unit/brain/test_input_contracts.py`.

No runtime, VPS, database, service, container, network, model, or temporary
source rollback applies because none may be changed.

## Stop conditions

Stop and return to governance if implementation requires a third path, Core
change, `BrainInferenceInvoker` change, provider change, serialization, broad
error hierarchy, business-specific intent, new non-standard dependency,
composition root, mapper/receiver implementation, live inference, or runtime
mutation. Architecture conflict or inability to satisfy the exact contract is
`BLOCKED`; a required third path is `SCOPE EXPANSION REQUIRED`.

## Preserved boundaries and debt

Core wiring, mapper implementation, Brain receiver implementation, production
composition, and production inference remain unauthorized. Composition debt
is unresolved. Preserve the Stage 0.8 and Stage 0.10 temporary staging sources;
cleanup remains separately governed.

## Project Owner approval

I, as Project Owner, authorize repository-only implementation of the Stage
0.11 BrainInput semantic boundary contract.

BrainInput shall carry only bounded immutable semantic intent,
provider-neutral data, identifiers, and optional opaque provenance references.

Core shall not supply prompts, provider configuration, timeout, output schema,
Memory, Specialist routing, or business-action authority through this
contract.

No Core wiring, mapper implementation, Brain receiver implementation,
composition, inference, or production activation is authorized.

## Publication, activation, and next action

The allowed governance diff is this package only. Publication requires a
normal clean, mergeable pull request into `main`, without force or history
rewrite. After merge and a synchronized clean-main audit, implementation
authority activates as:

`INTELLIGENCE STAGE 0.11 BRAININPUT CONTRACT IMPLEMENTATION APPROVED — READY TO BUILD`

The exact next official action is repository-only implementation and
verification of the two authorized paths. Activation itself writes no source,
runs no inference, and changes no runtime.
