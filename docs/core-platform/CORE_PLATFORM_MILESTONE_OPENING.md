# Core Platform Milestone Opening

## Record

| Field | Value |
|---|---|
| Milestone name | Core Platform |
| Phase name | Core Platform |
| Current status | **OPEN FOR FREEZE PREPARATION** |
| Project Owner approval | Explicitly approved on 2026-07-30 |

## Applicable Authority

- Blueprint: `docs/AIOS_ARCHITECTURE_v1.md`, activated from
  `origin/sprint-18-conversation-engine` at
  `e6ac77a3b287d839f6f8709da0c4652a332083c1`.
- Roadmap: `docs/AIOS_Roadmap_Frozen.md`, activated from
  `origin/sprint-18-conversation-engine` at
  `e6ac77a3b287d839f6f8709da0c4652a332083c1`.
- Governance: `docs/governance/GOVERNANCE_DECISION_001.md` and Active
  Governance Decisions GD-002 through GD-007 at
  `docs/governance/GOVERNANCE_DECISION_002.md` through
  `docs/governance/GOVERNANCE_DECISION_007.md`.
- Authority decision:
  `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md`.

## Domain Foundation Relationship

The existing
`docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` remains the
approved Domain Foundation authority for its published scope. Core Platform
must consume that boundary without moving application, persistence, dispatch,
transport, retry, or infrastructure behavior into the Domain Foundation.
Opening Core Platform for freeze preparation neither changes Domain Foundation
content nor represents every Foundation Roadmap row as completed.

## Core Platform Boundary

The milestone boundary is the Blueprint path through AIOS Core:

`Telegram Adapter boundary → Universal Ingestion → Request Context → Asset
Pipeline → Document Manifest → PostgreSQL Registry → AIOS Event Engine → AIOS
Core`

### Included Scope

- the named Core Platform path and its existing Telegram input boundary;
- Input Classifier, original-file storage, metadata, manifest, registry, Event
  Engine, and AIOS Core boundary work required by the active Blueprint;
- Blueprint dependency direction, source/runtime separation, and service
  requirements;
- the minimum evidence-required architecture contracts listed in the authority
  decision;
- planning, review, verification design, and freeze preparation.

### Explicit Exclusions

- AIOS Brain, Chief of Staff, Advisor, Decision Engine, Specialist Router,
  Memory, Knowledge, Planner, and Business Specialists;
- autonomous business logic, new business domains, new interfaces, and external
  integrations;
- unrelated deployment or production scope;
- source implementation, test implementation, runtime mutation, release,
  version change, and EF-07 within this opening record.

## Prerequisites and Readiness Evidence

Prerequisites for freeze preparation are satisfied by:

- the active Blueprint and Roadmap copies and their source provenance;
- the approved Domain Foundation Master relationship stated above;
- explicit Project Owner approval of GD-002 through GD-007;
- `docs/core-platform/EF01_CORE_PLATFORM_REPOSITORY_AUDIT.md`;
- `docs/core-platform/EF02_CORE_PLATFORM_BLUEPRINT_ALIGNMENT.md`;
- `docs/core-platform/EF03_CORE_PLATFORM_ROADMAP_ALIGNMENT.md`;
- `docs/core-platform/EF04_CORE_PLATFORM_GOVERNANCE_ALIGNMENT.md`;
- the revised
  `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1_DRAFT.md`; and
- the re-run `docs/core-platform/EF06_CORE_PLATFORM_EXECUTION_REVIEW.md`.

## Opening Conditions

- EF-06 may be completed against the authority recorded above.
- EF-07 may be performed only after EF-06 returns PASS.
- The milestone is open only for freeze preparation.
- Roadmap progress remains `Not Started`; this opening is not implementation,
  completion, verification, or release evidence.

## Implementation Conditions

Core Platform implementation remains prohibited until EF-07 successfully
freezes the plan. After freeze, implementation still requires every applicable
plan gate, approved minimum architecture contract, exact baseline, scoped
change authority, and other governance conditions recorded in the frozen plan.

**IMPLEMENTATION NOT YET AUTHORIZED**
