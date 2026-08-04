# AIOS Layer Architecture

| Field | Value |
|---|---|
| Document | `AIOS_LAYER_ARCHITECTURE.md` |
| Status | **ACTIVE** |
| Document class | Layer Authority |
| Approval authority | Project Owner |
| Effective authority | Current Layer Authority for the declared scope |

## Purpose

Define AIOS architecture layers, their responsibility boundaries, ownership, and allowed dependency direction without defining implementation or runtime behavior.

## Authority Sources

1. `docs/AIOS_ARCHITECTURE_v1.md` — Blueprint and highest Source of Truth.
2. `docs/architecture/AIOS_AUTHORITY_HIERARCHY.md` — Published Layer Authority scope and precedence material used for review without treating it as Active authority.
3. `docs/architecture/AIOS_CANONICAL_MODEL.md` — Active vocabulary authority.
4. Active Governance Decisions — only for governance and lifecycle treatment.

No implementation evidence is an authority source for this document.

## Scope

This document defines only:

- architecture layers;
- layer responsibility and boundary;
- architectural ownership;
- allowed and forbidden dependency direction; and
- producer, consumer, input, and output status where explicit authority exists.

## Non-Goals

This document does not define runtime behavior, workflow, orchestration, scheduling, routing, event dispatch, service implementation, API, database schema, persistence, protocol, adapter implementation, infrastructure, message broker, queue, cache, deployment, or implementation contract.

The Official Pipeline is not converted into runtime flow or dependency direction here. Its ordering does not create a dependency, producer, consumer, input, output, or ownership rule.

## Interpretation Rules

- `may depend on` and `may use` establish permission, not a mandatory dependency.
- A dependency not explicitly authorized by a source is **UNRESOLVED**.
- **UNRESOLVED** does not mean allowed or forbidden.
- Canonical Model items marked **UNRESOLVED** remain **UNRESOLVED**.
- Canonical Model items marked **OUT OF SCOPE** remain **OUT OF SCOPE**.
- No layer may promote or define a new canonical object.
- `Produces`, `Consumes`, `Input`, and `Output` concern canonical vocabulary only; they do not define runtime transfer.

## Layer Set

The layer set is limited to terms explicitly present in Blueprint architecture or dependency statements:

1. Adapter Layer
2. Ingestion Layer
3. App Layer
4. Storage Layer
5. Core Layer
6. Brain Layer
7. Specialist Layer

This classification adds no component or capability.

## 1. Adapter Layer

1. **Purpose:** Establish the architectural boundary for the Blueprint's Adapter term.
2. **Responsibility:** Contain the `Telegram Adapter` architectural placement while excluding business logic.
3. **Owns:** The Adapter-layer placement of `Telegram Adapter`; no implementation ownership is defined.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** **UNRESOLVED**.
6. **Input:** **UNRESOLVED**.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** Core Layer.
9. **Forbidden Dependencies:** Placement of business logic in `Telegram Adapter` is forbidden. Other dependency directions are **UNRESOLVED**.

## 2. Ingestion Layer

1. **Purpose:** Establish the architectural boundary for the Blueprint's Ingestion term.
2. **Responsibility:** Contain the architectural placement of `Universal Ingestion` and `Asset Pipeline` without defining their behavior.
3. **Owns:** The Ingestion-layer placement of those named components; no implementation ownership is defined.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** **UNRESOLVED**.
6. **Input:** **UNRESOLVED**.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** App Layer and Storage Layer.
9. **Forbidden Dependencies:** **UNRESOLVED**.

The term `Asset` remains **UNRESOLVED** under the Active Canonical Model. Placement of `Asset Pipeline` does not promote an Asset object.

## 3. App Layer

1. **Purpose:** Establish the architectural boundary for the Blueprint's App dependency target.
2. **Responsibility:** **UNRESOLVED** beyond its explicit position as an allowed dependency of Ingestion.
3. **Owns:** **UNRESOLVED**.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** **UNRESOLVED**.
6. **Input:** **UNRESOLVED**.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** **UNRESOLVED**.
9. **Forbidden Dependencies:** **UNRESOLVED**.

## 4. Storage Layer

1. **Purpose:** Establish the architectural boundary for the Blueprint's Storage term.
2. **Responsibility:** Limit Storage as a layer boundary without defining storage design or behavior.
3. **Owns:** The Storage architectural boundary; no implementation ownership is defined.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** **UNRESOLVED**.
6. **Input:** **UNRESOLVED**.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** **UNRESOLVED**.
9. **Forbidden Dependencies:** Brain Layer and Specialist Layer.

The prohibition means dependency direction must not point from Storage Layer toward Brain Layer or Specialist Layer. No persistence or infrastructure meaning is added.

## 5. Core Layer

1. **Purpose:** Establish the architectural boundary for `AIOS Core`.
2. **Responsibility:** Contain the architectural placement of `AIOS Core` without defining services or behavior.
3. **Owns:** The Core-layer placement of `AIOS Core`; no implementation ownership is defined.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** **UNRESOLVED**.
6. **Input:** **UNRESOLVED**.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** **UNRESOLVED**.
9. **Forbidden Dependencies:** **UNRESOLVED**.

Adapter Layer may depend on Core Layer, and Specialist Layer may use approved Core services. These permissions do not establish a reverse dependency.

## 6. Brain Layer

1. **Purpose:** Establish the architectural boundary for `AIOS Brain`.
2. **Responsibility:** Contain the Blueprint-named Brain components without defining their runtime behavior.
3. **Owns:** Architectural placement of `Chief of Staff`, `Advisor`, `Decision Engine`, `Specialist Router`, `AIOS Memory`, `Knowledge`, and `Planner`; no implementation ownership is defined.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** `Request Context`, `Manifest`, `Registry`, `Memory`, and `Knowledge`, using the Active Canonical Model's exact status and unresolved equivalences.
6. **Input:** **UNRESOLVED**; consumption does not establish an input contract.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** **UNRESOLVED**.
9. **Forbidden Dependencies:** **UNRESOLVED**.

This consumption statement creates no flow, routing, orchestration, service call, or implementation dependency.

## 7. Specialist Layer

1. **Purpose:** Establish the architectural boundary for `Specialists`.
2. **Responsibility:** Contain the architectural placement of the Blueprint-named Specialists without defining specialist behavior.
3. **Owns:** Architectural placement of `Admin`, `Finance`, `CTO`, `Content`, and `Creative`; no implementation ownership is defined.
4. **Produces:** **UNRESOLVED**.
5. **Consumes:** **UNRESOLVED**.
6. **Input:** **UNRESOLVED**.
7. **Output:** **UNRESOLVED**.
8. **Allowed Dependencies:** Approved Core services and business repositories, exactly as permitted by the Blueprint. This does not define either service or repository.
9. **Forbidden Dependencies:** **UNRESOLVED**.

## Dependency Direction

Only the following directions are authorized:

| Source layer | Direction | Target | Authority limit |
|---|---|---|---|
| Adapter Layer | may depend on | Core Layer | Permission only. |
| Ingestion Layer | may depend on | App Layer | Permission only. |
| Ingestion Layer | may depend on | Storage Layer | Permission only. |
| Specialist Layer | may use | approved Core services | Permission only; no service definition. |
| Specialist Layer | may use | business repositories | Permission only; no repository definition. |
| Storage Layer | must not depend on | Brain Layer | Explicit prohibition. |
| Storage Layer | must not depend on | Specialist Layer | Explicit prohibition. |

Every other dependency direction is **UNRESOLVED**.

## Canonical Object Boundary

| Canonical Model status | Layer treatment |
|---|---|
| Canonical | May be referenced only with its Active meaning. |
| **UNRESOLVED** | Remains **UNRESOLVED**; no layer may own, produce, consume, transform, or redefine it by inference. |
| **OUT OF SCOPE** | Remains **OUT OF SCOPE**. |

`DomainEvent` and `EventEnvelope` are Canonical, but their layer producer, consumer, input, output, ownership, and dependencies are **UNRESOLVED**. Event dispatch is outside scope.

## Final Architecture Review

Final Architecture Review was completed on 2026-08-03 against the Blueprint, Published Authority Hierarchy, Active Canonical Model, and active Governance Decisions.

The review confirmed:

- every layer term is traceable to Blueprint architecture or dependency language;
- every allowed or forbidden dependency is an exact preservation of a Blueprint dependency statement;
- Official Pipeline ordering was not converted into dependency or runtime behavior;
- canonical vocabulary status was preserved without promotion;
- missing ownership, producer, consumer, input, output, and dependency authority is marked **UNRESOLVED**;
- no capability, implementation, workflow, orchestration, scheduling, routing, event dispatch, schema, persistence, protocol, infrastructure, deployment, or implementation contract was added; and
- no Blueprint, Authority Hierarchy, Canonical Model, or Governance Decision was modified.

No substantive conflict was found within the declared scope.

## Approval Record

The Project Owner instruction dated 2026-08-03 explicitly approved Phase 2 and required transition through Proposed, Reviewed, Approved, Published, and Active after the stated review and lifecycle gates were satisfied. Those requirements are satisfied.

## Lifecycle History

| Date | Status | Record |
|---|---|---|
| 2026-08-03 | Draft | Initial layer-authority working content; no authority. |
| 2026-08-03 | Proposed | Content completed and submitted for Final Architecture Review. |
| 2026-08-03 | Reviewed | Final Architecture Review completed with no substantive conflict in scope. |
| 2026-08-03 | Approved | Project Owner approval applied after successful review. |
| 2026-08-03 | Published | Approved document and approval record accepted into repository history in commit `4c7eb10`. |
| 2026-08-03 | Active | Published document explicitly activated for its declared Layer Authority scope after publication commit `be2d1c8`. |

## Publication and Activation

The approved document and approval record entered accepted repository history in commit `4c7eb10`. Publication was explicitly recorded in commit `be2d1c8`. This document is now explicitly Active as current Layer Authority only for its declared scope.


## Stage 3.1.4 Scoped Layer Extension

| Field | Value |
|---|---|
| Status | **APPROVED — PUBLICATION PENDING** |
| Authority class | Existing Layer Authority |
| Accepted baseline | 91797b6b97176f96fc60787926d801311e59b15f |
| Scope | Stage 3.1.4 ownership consequences only |
| New layer/general dependency | None |

| Action | Owner layer | Producer | Consumer | Allowed direction | Prohibited reverse dependency | Communication |
|---|---|---|---|---|---|---|
| Register | Core Layer placement of PostgreSQL Registry | Ingestion Layer at completed Manifest boundary | Registry boundary | Ingestion to Core, Register handoff only | Registry cannot depend on Ingestion to own Receive through Create Manifest | manifest disposition in; registration disposition out |
| Process | Core Layer placement of AIOS Event Engine | Registry boundary | Event Engine boundary | Registry boundary to Event Engine boundary | Event Engine cannot depend on Registry to own registration/persistence | registered disposition in; event-delivery disposition out |
| Route | Core Layer placement of AIOS Core | Event Engine boundary | AIOS Core ending at Brain boundary | Event Engine boundary to AIOS Core | Core cannot depend on Event Engine to own delivery; no Brain/Specialist dependency | event-delivery in; downstream boundary disposition out |
| Respond | Adapter Layer, delivery only | Core Platform acknowledgement boundary | Telegram Adapter | Core Platform to Adapter, acknowledgement only | Adapter cannot own ingestion, Process, Route, Intelligence, specialist selection, or completed-response generation | acknowledgement in; delivery disposition out |

These are narrow communication permissions, not packages, services, calls,
workflow, runtime dependencies, or broader dependency authority. Brain and
Specialist Layers are not producer or consumer. Route ends at the Brain
boundary and is not Specialist Router.

### Extension Lifecycle

| Date | State | Evidence |
|---|---|---|
| 2026-08-05 | Draft | Prepared from accepted baseline; no authority effect. |
| 2026-08-05 | Proposed | Complete scoped content submitted for formal review; no authority effect. |
| 2026-08-05 | Reviewed | Authority, scope, dependency, canonical, phase, and prohibited-path review PASS against draft commit 605f860. |
| 2026-08-05 | Approved | Project Owner instruction explicitly approves execution of this scoped lifecycle after PASS review; publication remains pending accepted commit. |
