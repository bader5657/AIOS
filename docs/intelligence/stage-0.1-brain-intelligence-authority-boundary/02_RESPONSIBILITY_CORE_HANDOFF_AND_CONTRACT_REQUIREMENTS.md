# Responsibility, Core Handoff, and Contract Requirements

## Responsibility matrix

| Boundary | Current state | Owns / future approved direction | Does not own or become |
|---|---|---|---|
| AIOS Core | Implemented and verified | Stateless deterministic readiness routing from `EventEnvelope` to the sole positive `AIOS_BRAIN_BOUNDARY` marker | Brain, inference, prompts, provider/model selection, Specialists, business workflows |
| Intelligence Roadmap phase | Stage 0.1 governance only | Implementation program for future intelligence capability within Brain architecture | A canonical runtime layer, service, router, or implicit dependency |
| AIOS Brain | Architecturally defined; runtime absent | Future cognitive/orchestration and decision authority; interpretation/use of bounded inference results; separately approved coordination with Memory, Specialist Router, Planner, Advisor, and Chief of Staff | Raw provider implementation detail; a reopening of Core semantics |
| Inference/provider capability | Direction approved; contract/runtime absent | Bounded request → provider/model execution → structured bounded result | Core routing, transport, ingestion, Storage, Registry, Event Engine, Memory, Specialists, business or tool execution |
| Memory | Named future Brain capability; inactive | Only future separately approved persistent/context capability | Hidden prompt/response/embedding/session retention by inference |
| Specialist Router / Specialists | Architecturally named; inactive | Future Router-owned specialist selection and separately approved Specialist work | Model selection or direct inference-to-Specialist invocation |

## Stable Core boundary

`AIOS_BRAIN_BOUNDARY` remains the sole positive Core route target and means
eligible for future handoff. It is not a Brain instance, receiver call,
provider, model, or success from downstream execution.

Core Platform is not reopened. AIOS Core must not select providers/models,
invoke Specialists or business workflows, reinterpret inference output, or
gain ownership of downstream state.

## Future receiver requirements

The future receiver is owned conceptually by AIOS Brain orchestration. Its
exact component, API, object name, and implementation path remain contract-
gated. Before wiring, approved contracts must establish:

- explicit receiving owner and result destination;
- immutable bounded input;
- correlation reference;
- optional, explicitly permitted context/source references;
- timeout/deadline behavior;
- no implicit persistence;
- bounded success and failure semantics;
- no false success after failure;
- no automatic tool, Specialist, or business action; and
- no semantic or state ownership leakage back into AIOS Core.

## Future request-contract requirements

`REQUEST CONTRACT STATUS = REQUIREMENTS APPROVED; NAME/SCHEMA NOT APPROVED`

The contract evaluation must decide and bound:

- correlation ID;
- request/context reference without duplicating canonical business objects;
- permitted content or input reference;
- requested bounded inference capability;
- timeout or deadline;
- explicitly configured provider/model reference, if approved;
- contract schema/version; and
- validation, immutability, and sensitive-data rules.

No final class name or canonical object is created here.

## Future result-contract requirements

`RESULT CONTRACT STATUS = REQUIREMENTS APPROVED; NAME/SCHEMA NOT APPROVED`

The result contract must define:

- success/failure;
- structured bounded output;
- bounded failure code;
- provider/runtime metadata only where allowed;
- approved model identifier only where allowed;
- duration;
- correlation ID; and
- validation of malformed or partial provider output.

The result returns to Brain-owned orchestration. AIOS Core must not semantically
reinterpret it. No final result class or canonical object is created here.
