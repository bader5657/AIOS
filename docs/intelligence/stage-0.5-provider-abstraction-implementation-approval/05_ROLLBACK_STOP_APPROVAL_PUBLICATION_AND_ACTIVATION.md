# Rollback, Stop Conditions, Approval, Publication, and Activation

## Repository-only rollback

If implementation cannot pass its gates, revert/remove only:

- `core/brain/provider.py`; and
- `tests/unit/brain/test_provider.py`.

There is no runtime, provider/model, VPS, database, service, network,
credential, or production rollback because none may change or activate.

## Mandatory stop conditions

Implementation must stop rather than widen scope if:

- Core semantics/files or frozen architecture must change;
- a provider adapter/runtime/model implementation becomes necessary;
- any third implementation path is required;
- a new dependency is required;
- runtime configuration format or resource controller must be invented;
- credentials, network, subprocess, filesystem, or local-runtime authority is
  necessary; or
- the exact Stage 0.4 interface/descriptor invariants cannot be represented.

An additional path yields
`INTELLIGENCE STAGE 0.5 SCOPE EXPANSION REQUIRED`; an unresolvable authority or
contract conflict yields `INTELLIGENCE STAGE 0.5 BLOCKED`.

## Project Owner approval

I, as Project Owner, authorize implementation of the minimal Brain-owned provider abstraction only:

- InferenceProvider
- ProviderDescriptor
- ProviderRuntimeKind
- focused tests

No provider/model/runtime selection, installation, network execution, local model execution, credentials, retry, persistence, Core modification, or production mutation is authorized.

## Publication and activation

- governance branch:
  `governance/intelligence-stage-0.5-provider-abstraction-implementation-approval`;
- allowed governance diff: this Stage 0.5 package only;
- governance PR: normal CLEAN/MERGEABLE pull request into `main`;
- source/test/dependency/service/VERSION effect: none;
- force/history rewrite: none;
- provider/model/runtime/network/production/VPS action: none.

Merging this governance PR activates implementation authority only. It does not
activate Brain, a provider adapter, network access, a local runtime, model
execution, credentials, persistence, retry, or production behavior.

Post-merge audit must confirm synchronized clean `main`, governance-only diff,
unchanged source/tests/Core/dependencies/service/VERSION, package presence, and
no provider/model/runtime/VPS artifact or action.

## Next official action

After governance activation:

`Intelligence Stage 0.5 — implement exactly core/brain/provider.py and tests/unit/brain/test_provider.py, then execute the approved verification gates.`

No provider/model may be selected, installed, configured, or executed in that
implementation workflow.
