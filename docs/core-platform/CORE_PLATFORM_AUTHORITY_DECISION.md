# Core Platform Authority Decision

## Status

**APPROVED**

**ACTIVE FOR CORE PLATFORM**

## Authority

Project Owner approval recorded on 2026-07-30.

## Decisions

1. **Blueprint and Roadmap activation.** The exact historical contents of the
   following artifacts are activated for Core Platform:

   | Authority | Historical source path | Source branch | Source commit | Active path | Scope |
   |---|---|---|---|---|---|
   | Blueprint | `docs/AIOS_ARCHITECTURE_v1.md` | `origin/sprint-18-conversation-engine` | `e6ac77a3b287d839f6f8709da0c4652a332083c1` | `docs/AIOS_ARCHITECTURE_v1.md` | Core Platform architecture planning and implementation, subject to the Domain Foundation Master and approved governance hierarchy |
   | Roadmap | `docs/AIOS_Roadmap_Frozen.md` | `origin/sprint-18-conversation-engine` | `e6ac77a3b287d839f6f8709da0c4652a332083c1` | `docs/AIOS_Roadmap_Frozen.md` | Core Platform phase order, scope, and progress governance, subject to the Blueprint, Domain Foundation Master, and approved governance hierarchy |

   The current-main copies preserve the historical contents exactly. Their
   lifecycle status is Approved, Published upon acceptance into repository
   history, and Active for the scope stated above.

2. **Early architecture contracts.** Minimum Core Platform contracts already
   required by repository evidence must be the earliest evidence-supported
   deliverables in
   `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1_DRAFT.md` and must be
   completed before dependent implementation. This is limited to the Core
   Platform boundary; package/module boundaries; dependency direction;
   configuration, lifecycle, and persistence ownership; communication-adapter,
   error/logging, validation, and service-behavior boundaries. It authorizes no
   speculative architecture or later-phase scope.

3. **Governance approval.** Governance Decisions GD-002 through GD-007 at
   `docs/governance/GOVERNANCE_DECISION_002.md` through
   `docs/governance/GOVERNANCE_DECISION_007.md` are explicitly approved and
   Active for their declared scopes. Their approved substance is unchanged.

4. **Milestone opening.** The Core Platform milestone is opened only for freeze
   preparation under
   `docs/core-platform/CORE_PLATFORM_MILESTONE_OPENING.md`.

## Limits

This authority is limited to activating the applicable Blueprint and Roadmap,
approving GD-002 through GD-007, authorizing early architecture-contract
deliverables, and opening the Core Platform milestone for freeze preparation.
It does not authorize AI Pipeline, Brain, Specialist Router, Business
Specialists, autonomous business logic, unrelated deployment or production
scope, EF-07 execution, or Core Platform implementation.

**IMPLEMENTATION NOT YET AUTHORIZED**
