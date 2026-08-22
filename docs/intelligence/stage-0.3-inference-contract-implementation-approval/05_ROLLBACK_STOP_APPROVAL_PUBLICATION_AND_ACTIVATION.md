# Rollback, Stop Conditions, Approval, Publication, and Activation

## Implementation rollback

Rollback is repository-only. If implementation cannot pass its gates, revert
or remove only these authorized additions:

- `core/brain/__init__.py`;
- `core/brain/inference_contracts.py`; and
- `tests/unit/brain/test_inference_contracts.py`.

There is no runtime, VPS, database, service, provider, model, migration,
credential, or production rollback because none may be changed or activated.

## Mandatory stop conditions

Implementation must stop and report the applicable blocker rather than widen
scope if:

- frozen architecture or Core semantics must change;
- provider/model implementation or selection becomes necessary;
- a new dependency or fourth implementation path is required;
- Brain package ownership conflicts with active authority;
- exact v1 schema cannot satisfy the Stage 0.2 invariants;
- Core would need to import Brain or production wiring/service behavior would
  change; or
- provider-native/raw content, persistence, Memory, Specialist, tools, or
  business semantics become necessary.

A required extra path yields
`INTELLIGENCE STAGE 0.3 SCOPE EXPANSION REQUIRED`; an authority or invariant
conflict that cannot be resolved inside the approved scope yields
`INTELLIGENCE STAGE 0.3 BLOCKED`.

## Project Owner approval

I, as Project Owner, authorize implementation of the approved Stage 0.2 Brain-owned inference contracts and focused tests only.

The implementation must remain provider-neutral, stateless, non-canonical, immutable, fail-closed, dependency-light, and must not modify Core Platform or production runtime behavior.

No provider/model installation or Brain activation is authorized.

## Publication

- governance branch:
  `governance/intelligence-stage-0.3-inference-contract-implementation-approval`;
- allowed governance diff: this Stage 0.3 package only;
- governance PR: normal CLEAN/MERGEABLE pull request into `main`;
- force push/history rewrite: prohibited;
- implementation paths: approved for a later, separate implementation change,
  not this governance PR;
- VERSION/release effect: none;
- production/VPS effect: none.

After governance merge, a post-merge audit must confirm clean synchronized
`main`, package-only governance diff, unchanged source/tests/runtime/service,
and no provider/model/VPS artifact or action.

## Activation and next action

Merging this governance PR activates implementation authority only. It does
not activate Brain, import Brain from Core, invoke a model, or alter production
behavior.

Next official action after governance activation:

`Intelligence Stage 0.3 — implement the three authorized contract/test paths, then execute the approved verification gates.`

Approval disposition:

`INTELLIGENCE STAGE 0.3 CONTRACT IMPLEMENTATION APPROVED — READY TO BUILD`
