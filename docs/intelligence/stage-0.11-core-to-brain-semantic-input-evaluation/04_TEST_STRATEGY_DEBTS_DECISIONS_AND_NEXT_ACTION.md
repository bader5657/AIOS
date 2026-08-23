# Test Strategy, Debts, Decisions, and Next Action

## Future unit and static test strategy

Implementation approval must require tests for:

- exact seven fields, types, defaults, and schema version;
- frozen/slotted and recursively immutable behavior;
- all identifier, intent, reference, container, and encoded-size bounds;
- no coercion and fail-closed unknown-field handling;
- exclusive correlation/request ID ownership and exact propagation;
- no provider/model/runtime configuration;
- no whole `CoreRouteResult`, `EventEnvelope`, Manifest, Registry row, Memory,
  Specialist, or business object/field;
- no content logging or persistence surface;
- readiness and semantic-source mapping correctness;
- invalid construction and ID mismatch fail before inference;
- Brain intent-policy mapping into unchanged invoker arguments;
- exact one-call result path and dependency/import direction; and
- static absence of Core imports in Brain contracts/receiver and Brain imports
  in `AIOSCore`.

## Future change inventory

Future implementation requires one new Brain-owned contract file, one explicit
boundary mapper, and one small Brain receiver. `AIOSCore.route`,
`CoreRouteResult`, `EventEnvelope`, `InferenceRequest`, and
`BrainInferenceInvoker` require no field or signature change. Exact mapper and
receiver modules, boundary failure taxonomy, and intent-policy registry are
implementation-approval subjects.

## Preserved debt and temporary sources

Production/outer Brain composition remains unresolved and is not solved here.
Preserve `/opt/aios/runtime/intelligence/staging/stage-0.8-src` and
`/opt/aios/runtime/intelligence/staging/stage-0.10-src`; cleanup requires
separate authority.

## Project Owner decisions required

The implementation approval must explicitly ratify:

1. name `BrainInput`;
2. Brain ownership and `core/brain/input_contracts.py` location;
3. exact five required and two optional fields;
4. Core supplies intent/data while Brain owns instruction, timeout, and schema;
5. originating context owns correlation ID and boundary mapper owns request ID;
6. explicit boundary mapper and small Brain receiver responsibilities;
7. no v1 `to_dict`/`from_dict`; and
8. a separately bounded pre-inference boundary failure taxonomy and intent
   vocabulary in implementation approval.

No architecture change is required. No implementation blocker exists once
these decisions are approved.

## Recommended next action

Create:

`Intelligence Stage 0.11 — Core-to-Brain Semantic Input Contract Implementation Approval`

That package must freeze exact APIs, modules, failure contract, intent test
vocabulary, file/test scope, rollback, and activation gates before any code is
written. It must not authorize production composition, live inference, or
runtime wiring.
