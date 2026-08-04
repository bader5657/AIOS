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

5. **Stage 3.1.3 capability contract boundaries.** The following boundaries close only the capability-contract authority gaps identified for Stage 3, Main Step 3.1, Sub Step 3.1.3. They add no capability beyond the Universal Ingestion inputs named by the Blueprint and do not define implementation.

### Web Link Validation

- **Validator:** Input Classifier is the Web Link validator.
- **Scope:** validation is limited to deciding whether a candidate value is within the Active Canonical Model `Web Link` recognition boundary.
- **Input:** one candidate value presented for `Web Link` recognition.
- **Output:** a validation result stating whether the candidate is within that recognition boundary; the result does not create a normalized or replacement value.
- **Ownership:** Input Classifier owns the validation decision; Universal Ingestion owns only the ingestion-side use of that bounded result.
- **Lifecycle boundary:** validation belongs to acceptance at `Receive` and grants no ownership of `Store Original`, `Extract Metadata`, `Create Manifest`, `Register`, `Process`, `Route`, or `Respond`.

This contract defines no regex, algorithm, parser, normalization rule, redirect treatment, or implementation.

### Mixed Telegram Input

- **Communication boundary:** Telegram Adapter owns transport receipt and hands the received Telegram message across the existing communication boundary to Universal Ingestion.
- **Ownership:** Telegram Adapter owns only transport communication; Universal Ingestion owns the ingestion contract at the receiving side of that boundary.
- **Multiple-media contract:** when the received Telegram message exposes more than one media input, the handoff contract preserves the presence and distinct identity of every recognized media input. This contract does not collapse the authority boundary to a single-media assumption.
- **Lifecycle boundary:** this contract is limited to `Receive`; ownership of later lifecycle steps remains governed separately.

This contract defines no precedence, ordering, aggregation, fallback, selection, deduplication, or runtime implementation.

### Audio Storage

- **Persistence ownership:** Storage owns persistence of original `Audio`.
- **Storage responsibility:** Storage is responsible only for preserving the original `Audio` through the persistence boundary.
- **Handoff boundary:** Universal Ingestion owns the `Store Original` request and hands the original `Audio` to Storage; Storage returns only a bounded persistence result to Universal Ingestion.

This contract defines no path, folder, filename, storage layout, storage mechanism, or storage implementation.

### Video Storage

- **Persistence ownership:** Storage owns persistence of original `Video`.
- **Storage responsibility:** Storage is responsible only for preserving the original `Video` through the persistence boundary.
- **Handoff boundary:** Universal Ingestion owns the `Store Original` request and hands the original `Video` to Storage; Storage returns only a bounded persistence result to Universal Ingestion.

This contract defines no path, folder, filename, storage layout, storage mechanism, or storage implementation.

## Stage 3.1.3 Authority Trace

| Blocker | Authority owner | Authority basis | Boundary result |
|---|---|---|---|
| Web Link recognition identity | Active Canonical Model | Blueprint names `Web link`; Canonical Model governs vocabulary and recognition | Canonical identity is established without a validation algorithm. |
| YouTube Link recognition identity and supported hosts | Active Canonical Model | Blueprint names `YouTube link`; Canonical Model governs vocabulary and recognition | Canonical identity and complete supported-host set are established without matching behavior. |
| Audio recognition identity | Active Canonical Model | Blueprint names `Audio`; Canonical Model governs vocabulary and recognition | Canonical identity is established without format or processing detail. |
| Video recognition identity | Active Canonical Model | Blueprint names `Video`; Canonical Model governs vocabulary and recognition | Canonical identity is established without format or processing detail. |
| Web Link Validation | Input Classifier | This Active Core Platform Authority Decision | Validator, scope, input, output, ownership, and lifecycle boundary are established. |
| Mixed Telegram Input | Telegram Adapter and Universal Ingestion at their communication boundary | Blueprint adapter restriction; Stage 3.1.2 ownership evidence; this Active decision | Communication ownership, multiple-media contract, and lifecycle boundary are established. |
| Audio Storage | Storage, with Universal Ingestion owning the ingestion handoff | Blueprint `Store Original`; Stage 3.1.2 ownership evidence; this Active decision | Persistence ownership, responsibility, and handoff boundary are established. |
| Video Storage | Storage, with Universal Ingestion owning the ingestion handoff | Blueprint `Store Original`; Stage 3.1.2 ownership evidence; this Active decision | Persistence ownership, responsibility, and handoff boundary are established. |

Full Authority Trace confirms that these decisions do not change the Official Pipeline, dependency directions, layer set or ownership established by the Layer Architecture, Blueprint, Authority Hierarchy, Frozen Roadmap, or Execution Plan order. They create no runtime behavior, ADR, new authority document, parser, validation algorithm, normalization rule, storage layout, or implementation detail.

## Limits

This authority is limited to activating the applicable Blueprint and Roadmap,
approving GD-002 through GD-007, authorizing early architecture-contract
deliverables, opening the Core Platform milestone for freeze preparation, and
establishing the Stage 3.1.3 capability-contract boundaries stated above.
It does not authorize AI Pipeline, Brain, Specialist Router, Business
Specialists, autonomous business logic, unrelated deployment or production
scope, EF-07 execution, or Core Platform implementation.

**IMPLEMENTATION NOT YET AUTHORIZED**


## Stage 3.1.4 Scoped Authority Extension

| Field | Value |
|---|---|
| Status | **APPROVED — PUBLICATION PENDING** |
| Authority class | Existing Core Platform Authority Decision |
| Project Owner instruction | 2026-08-05 |
| Accepted source baseline | 91797b6b97176f96fc60787926d801311e59b15f |
| Scope | Stage 3.1.4 prerequisite authority only |
| Implementation effect | None |

This extension defines action ownership and minimum boundaries only. Accepted
input and produced output below are non-canonical boundary dispositions, not
runtime types, schemas, payloads, records, or objects. Success permits only the
named next handoff. Failure means no downstream success is claimed and the
lifecycle stops at the current boundary. No retry, exception, compensation,
workflow, algorithm, API, transaction, or implementation is defined.

| Action | Owner | Accepted input | Produced output | Handoff | Success/failure and stop |
|---|---|---|---|---|---|
| Receive | Universal Ingestion at receiving side; Telegram Adapter owns transport receipt | Telegram transport input | bounded acceptance disposition | Adapter to Universal Ingestion | success may proceed; failure stops before storage |
| Store Original | Storage; Universal Ingestion owns request only | accepted original input where applicable | original-preservation disposition | Ingestion to Storage and bounded return | failure stops before Metadata |
| Extract Metadata | Metadata Engine; Universal Ingestion owns request only | successful preservation disposition | metadata disposition | Ingestion to Metadata Engine and bounded return | failure stops before Manifest |
| Create Manifest | Document Manifest boundary; Universal Ingestion owns request only | accepted upstream dispositions | completed Document Manifest boundary disposition | Ingestion to Document Manifest boundary | failure stops before Register |
| Register | PostgreSQL Registry | completed Document Manifest disposition | bounded registration disposition | Stage 3.1.4 exposes handoff toward Registry | stop before Registry runtime, transaction, schema, migration, and Stage 5 behavior |
| Process | AIOS Event Engine | bounded registered disposition | bounded event-delivery disposition toward AIOS Core | Registry boundary to Event Engine boundary to Core boundary | failure makes no Route-success claim; stop before Event Engine runtime and Stage 6 behavior |
| Route | AIOS Core | bounded event-delivery disposition | bounded downstream disposition at AIOS Brain boundary | Event Engine boundary to AIOS Core to Brain boundary | failure makes no Respond-completed claim; clarification is later Intelligence; stop before Brain, Specialist Router, Specialists, and Stage 7+ downstream behavior |
| Respond | Telegram Adapter, transport delivery only | bounded acknowledgement disposition | acknowledgement delivery disposition | Core Platform acknowledgement boundary to Adapter | delivery failure makes no delivered-acknowledgement claim; stop before completed business response |

PostgreSQL Registry is the bounded owner of Register. Stage 3.1.4 produces only
its bounded handoff and runs no Registry behavior.

AIOS Event Engine is the bounded owner of Process. This explicit Project Owner
decision preserves the accepted Registry, Event Engine, Core order and grants
no Event Engine implementation authority.

AIOS Core is the bounded owner of Route. Route is explicitly not equivalent to
Specialist Router. Universal Ingestion has no routing authority. Clarification
remains later Intelligence and is not produced here.

Telegram Adapter owns acknowledgement delivery only. Acknowledgement confirms
receipt or bounded handoff; delivery is the transport act; completed business
response is downstream business or Intelligence output and is outside scope.

This mapping preserves the Official Pipeline and Universal Ingestion lifecycle
orders. Stage 3.1.4 stops before Registry runtime, Event Engine runtime, AIOS
Core downstream implementation, Brain, Specialist Router, Specialists,
completed-response generation, and all Stage 5+ implementation.

No Canonical Model extension is required. No Response, Registry Entry, process
result, routing decision, Asset, Event, Message, or Task object is created.

### Extension Lifecycle

| Date | State | Evidence |
|---|---|---|
| 2026-08-05 | Draft | Prepared from accepted baseline; no authority effect. |
| 2026-08-05 | Proposed | Complete scoped content submitted for formal review; no authority effect. |
| 2026-08-05 | Reviewed | Authority, scope, dependency, canonical, phase, and prohibited-path review PASS against draft commit 605f860. |
| 2026-08-05 | Approved | Project Owner instruction explicitly approves execution of this scoped lifecycle after PASS review; publication remains pending accepted commit. |
