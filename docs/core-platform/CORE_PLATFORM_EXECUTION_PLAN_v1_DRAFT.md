# Core Platform Execution Plan v1 — DRAFT

## Document Status

| Field | Value |
|---|---|
| Document | Core Platform Execution Plan v1 |
| Status | **APPROVED FOR FREEZE** |
| Review status | **EF-06 PASS — ELIGIBLE FOR EF-07** |
| Repository baseline | `a90ac183a1677e5bc82dd3e8200d28420b9240cd` |
| Blueprint baseline | Active `docs/AIOS_ARCHITECTURE_v1.md`; exact source `e6ac77a3b287d839f6f8709da0c4652a332083c1:docs/AIOS_ARCHITECTURE_v1.md` |
| Roadmap baseline | Active `docs/AIOS_Roadmap_Frozen.md`; exact source `e6ac77a3b287d839f6f8709da0c4652a332083c1:docs/AIOS_Roadmap_Frozen.md` |
| Governance baseline | Active GD-002 through GD-007 plus GD-001 |
| Product version | `0.1.0-alpha` |
| Implementation authority | **Not established** |
| Project Owner approval | **Recorded for freeze preparation; not implementation** |

This document is an execution-plan draft approved for EF-07 freeze review. It
does not implement, test, merge, release, version, or deploy Core Platform. No
implementation stage may begin merely because this draft exists.

**NOT YET FROZEN**

**NOT YET AUTHORIZED FOR IMPLEMENTATION**

## Purpose

Define a controlled execution sequence for Core Platform that remains aligned
with:

1. the frozen Blueprint;
2. the frozen Roadmap;
3. the recorded status and authority limits of Governance Framework v1; and
4. the current repository and its historical branch evidence.

The plan converts EF-01 through EF-04 findings into gated future work. It does
not change the scope established by the Blueprint or Roadmap.

## Authority and Evidence

- Repository audit:
  `docs/core-platform/EF01_CORE_PLATFORM_REPOSITORY_AUDIT.md`
- Blueprint alignment:
  `docs/core-platform/EF02_CORE_PLATFORM_BLUEPRINT_ALIGNMENT.md`
- Roadmap alignment:
  `docs/core-platform/EF03_CORE_PLATFORM_ROADMAP_ALIGNMENT.md`
- Governance alignment:
  `docs/core-platform/EF04_CORE_PLATFORM_GOVERNANCE_ALIGNMENT.md`
- Frozen Blueprint:
  active `docs/AIOS_ARCHITECTURE_v1.md`, sourced exactly from
  `e6ac77a3b287d839f6f8709da0c4652a332083c1:docs/AIOS_ARCHITECTURE_v1.md`
- Frozen Roadmap:
  active `docs/AIOS_Roadmap_Frozen.md`, sourced exactly from
  `e6ac77a3b287d839f6f8709da0c4652a332083c1:docs/AIOS_Roadmap_Frozen.md`
- Project Owner authority:
  `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md`
- Milestone opening:
  `docs/core-platform/CORE_PLATFORM_MILESTONE_OPENING.md`
- Governance Framework Freeze:
  `docs/governance/GOVERNANCE_FRAMEWORK_FREEZE_v1.md`
- Governance Decisions:
  `docs/governance/GOVERNANCE_DECISION_001.md` through
  `docs/governance/GOVERNANCE_DECISION_007.md`
- Domain Foundation authority:
  `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md`
- Release Review:
  `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md`
- Repository status evidence:
  `README.md`, `CHANGELOG.md`, `VERSION`, `core/`, `config/`, `docker/`,
  `scripts/`, and `tests/`

The Blueprint and Roadmap are present as exact current-main copies of the
historical artifacts at commit
`e6ac77a3b287d839f6f8709da0c4652a332083c1` and are Active for Core Platform.
GD-002 through GD-007 are approved and Active for their declared scopes by
explicit Project Owner approval. The Governance Framework Freeze did not grant
that approval.

## Controlling Findings

1. Core Platform is next by Frozen Roadmap order, after Foundation and before
   Intelligence, but readiness and active milestone status are not established
   (`EF03_CORE_PLATFORM_ROADMAP_ALIGNMENT.md:289-313`).
2. Current `HEAD` is not fully aligned with the Blueprint. Asset Pipeline,
   PostgreSQL Registry, Event Engine runtime, and an identifiable AIOS Core
   boundary are missing
   (`EF02_CORE_PLATFORM_BLUEPRINT_ALIGNMENT.md:200-223`).
3. Request Context, ingestion, manifest, storage, PostgreSQL responsibility,
   and Mission Control are partially aligned
   (`EF02_CORE_PLATFORM_BLUEPRINT_ALIGNMENT.md:98-110`).
4. Historical Asset Pipeline, Registry, and Event Engine implementations exist
   on `origin/sprint-18-conversation-engine`, but are not current `main`
   implementation
   (`EF01_CORE_PLATFORM_REPOSITORY_AUDIT.md:218-223`).
5. Governance Framework v1 is internally consistent; GD-002 through GD-007 are
   now approved and Active, but no governance decision authorizes Core Platform
   implementation.
6. The Project Owner has activated the exact historical Blueprint and Roadmap,
   opened Core Platform for freeze preparation, and authorized the minimum
   evidence-required architecture contracts as pre-implementation deliverables.

## Execution Rules

Every Stage, Main Step, and Sub Step below must satisfy all four columns in its
row before it may advance:

| Control | Requirement |
|---|---|
| Blueprint | Work must implement or verify an explicitly named Blueprint capability, lifecycle step, boundary, dependency rule, or operational requirement. Missing detail must stop work; it must not be invented. |
| Roadmap | Work must remain inside Core Platform, follow Foundation, precede Intelligence and later phases, add no Roadmap scope, and support status updates only after completion and verification. |
| Governance | Work requires explicit Project Owner authority, declared scope, controlled artifact/branch treatment, verification, release approval when applicable, and no inferred version change. Draft governance decisions must not be represented as active unless explicitly approved or adopted for the work. |
| Repository | Work must begin from an exact accepted baseline, preserve current verified assets, distinguish current `main` from historical branch code, add tests proportional to change, and produce traceable evidence. |

If any one column is unsatisfied, the applicable Sub Step stops.

## Core Platform Boundary

This plan binds only the Core Platform phase. It does not govern Foundation,
Intelligence, Business Capability, Interfaces, External Integrations, or any
later AIOS phase. Its use of the existing Telegram Adapter is limited to the
input boundary and verification of the Blueprint pipeline; it does not add a
new interface milestone.

### Included Scope

The Blueprint’s official platform path through AIOS Core:

```text
Telegram Adapter boundary
→ Universal Ingestion
→ Request Context
→ Asset Pipeline
→ Document Manifest
→ PostgreSQL Registry
→ AIOS Event Engine
→ AIOS Core
```

Supporting requirements included only where the Blueprint explicitly connects
them to this path:

- Input Classifier;
- original-file storage;
- Metadata Engine;
- ingestion lifecycle;
- PostgreSQL metadata responsibility;
- dependency direction;
- systemd operational requirements;
- end-to-end verification through the existing Telegram boundary.

Evidence:
`e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:27-53`,
`e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:99-169`,
`e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:215-227`.

### Explicit Exclusions

- AIOS Brain;
- Chief of Staff;
- Advisor;
- Decision Engine;
- Specialist Router behavior;
- AIOS Memory;
- Knowledge;
- Planner;
- business specialists;
- new interfaces;
- external integrations;
- new business domains;
- Blueprint, Roadmap, or governance redesign;
- automatic product-version change.

These belong to later or separate Blueprint/Roadmap boundaries. No excluded
item may be pulled into Core Platform through this plan.

## Stage 0 — Authority and Baseline Gate

No implementation Stage may start until every Stage 0 exit condition is
satisfied.

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 0.1 Confirm authority baselines | 0.1.1 Verify the activated Blueprint copy against its exact historical source | Confirms architecture authority without inventing detail | Does not alter Roadmap scope | Applies explicit Project Owner activation | Compares `docs/AIOS_ARCHITECTURE_v1.md` byte-for-byte with commit `e6ac77a3b` | Exact-content verification and authority decision |
| 0.1 Confirm authority baselines | 0.1.2 Verify the activated Roadmap copy against its exact historical source | Preserves Blueprint as design authority | Confirms Core Platform order and scope without editing Roadmap | Applies explicit Project Owner activation | Compares `docs/AIOS_Roadmap_Frozen.md` byte-for-byte with commit `e6ac77a3b` | Exact-content verification and authority decision |
| 0.2 Resolve governance applicability | 0.2.1 Record GD-002 through GD-007 as approved and Active for their declared scopes | Does not change architecture | Does not change milestone content | Applies explicit Project Owner approval without expanding substance | Uses exact decision statuses in current `HEAD` | Approved governance decisions and authority decision |
| 0.2 Resolve governance applicability | 0.2.2 Record explicit Project Owner implementation authority | Limits authority to Blueprint-named Core Platform work | Authorizes no later Roadmap phase | Satisfies authority gate; approval must be scope-limited | Establishes permission for future repository changes | Accepted implementation approval naming scope, targets, exclusions, and baseline |
| 0.3 Establish milestone readiness | 0.3.1 Record the Domain Foundation relationship and freeze-preparation readiness without claiming all Foundation rows complete | Does not add Core Platform design | Honors Foundation-before-Core-Platform order and preserves Roadmap status | Applies the scope-limited milestone decision | Reconciles approved Domain Foundation scope with remaining Foundation status | Accepted milestone-opening record |
| 0.3 Establish milestone readiness | 0.3.2 Open Core Platform only for freeze preparation with declared scope | Uses only the official Blueprint path | Opens the next named phase without changing Roadmap progress | Applies GD-006 and explicit Project Owner approval | Creates a traceable pre-implementation scope boundary | `CORE_PLATFORM_MILESTONE_OPENING.md` |
| 0.4 Establish change controls | 0.4.1 Create a scoped Core Platform Change Request | Names only Blueprint capabilities | Adds no Roadmap item | Records targets, classification, rationale, and requested authority | Identifies exact repository files/packages expected to be affected | Accepted scoped Change Request |
| 0.4 Establish change controls | 0.4.2 Approve branch, review, merge, and verification procedure | Preserves dependency and architecture review gates | Prevents unverified status advancement | Resolves currently undefined branch/PR procedures | Identifies target branch and accepted baseline; historical branches remain non-current | Project Owner-approved working procedure |
| 0.4 Establish change controls | 0.4.3 Create and approve the minimum evidence-required architecture contracts before dependent implementation: Core Platform and package/module boundaries; dependency direction; configuration, lifecycle, persistence, communication-adapter, error/logging, validation, and service-behavior ownership and boundaries | Prohibits invented Blueprint behavior and later-phase design | Prohibits scope addition during implementation | Uses the Project Owner’s early-contract authorization; unresolved or expanded scope stops for further authority | Makes contracts the earliest deliverables and prevents speculative code | Approved contract set, evidence traceability, and explicit stop record for anything not supported |

### Stage 0 exit gate

- Blueprint and Roadmap baselines explicitly confirmed.
- Governance applicability explicitly recorded.
- Foundation readiness resolved.
- Core Platform milestone explicitly opened.
- Scoped implementation approval recorded.
- Change, branch, review, merge, and verification process approved.
- Minimum evidence-required architecture contracts completed and approved
  before any dependent implementation step.
- No unresolved authority contradiction.

Failure of any condition stops the plan before implementation.

## Stage 1 — Current Baseline Reconciliation

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 1.1 Freeze execution baseline | 1.1.1 Record exact `main` commit, clean tracked state, and accepted untracked-document treatment | Creates no architecture change | Creates no progress claim | Establishes the implementation baseline | Prevents later evidence from mixing baselines | Baseline record and working-tree inventory |
| 1.1 Freeze execution baseline | 1.1.2 Inventory current platform packages, schemas, dependencies, and tests | Maps official pipeline capabilities | Stays within Core Platform | Review evidence only; no approval inferred | Revalidates EF-01 against execution baseline | Signed/reviewed inventory |
| 1.2 Reconcile historical implementations | 1.2.1 Review historical Asset Pipeline code against current authority | Evaluates only Blueprint Asset Pipeline | Does not mark Roadmap progress | Historical branch is non-authoritative until explicitly accepted | Compares commit `9d1288c` code with current contracts; no blind copy/merge | Component disposition: reuse, adapt, or reject, with evidence |
| 1.2 Reconcile historical implementations | 1.2.2 Review historical Registry code against current authority | Evaluates only PostgreSQL Registry | Does not mark Roadmap progress | Same branch/authority controls | Compares commit `d58c1c3` with current baseline | Component disposition with evidence |
| 1.2 Reconcile historical implementations | 1.2.3 Review historical Event Engine code against current authority | Evaluates only AIOS Event Engine | Does not mark Roadmap progress | Same branch/authority controls | Compares commit `c56e046` with current DomainEvent/EventEnvelope boundary | Component disposition with evidence |
| 1.3 Establish verification baseline | 1.3.1 Define one repository-root test command that discovers current tests | Supports stage verification | Enables evidence before status update | Verification command is reviewed and accepted | Resolves current zero-test root-discovery risk | Command record with expected suite inventory |
| 1.3 Establish verification baseline | 1.3.2 Record current functional and dependency-boundary results | Verifies current Blueprint-aligned behavior | Does not advance status | Establishes pre-change evidence | Preserves 212-test Domain Foundation baseline and identifies uncovered packages | Baseline verification report |
| 1.4 Verify retained named capabilities | 1.4.1 Verify the existing Telegram boundary and Input Classifier against the explicit Blueprint inputs without adding adapter business logic | Preserves named completed capabilities and adapter rule | Boundary verification only; no Interfaces-phase expansion | Verification creates no implementation authority | Uses `core/adapters/telegram/main.py` and `core/app/input_classifier.py` | Focused tests and dependency review |
| 1.4 Verify retained named capabilities | 1.4.2 Verify Mission Control v1 only to the behavior evidenced by `core/mission/status.py`; stop if additional behavior is required | Preserves a Blueprint-named completed capability without inventing its contract | Core Platform supporting verification only | Missing behavior requires architecture authority | Uses current implementation and records its unverifiable limits | Focused tests plus authority finding |

### Stage 1 exit gate

- Exact execution baseline recorded.
- Every historical implementation has an explicit disposition.
- No historical branch content is represented as current code.
- A reliable test and verification baseline exists.
- Existing Telegram boundary, Input Classifier, and evidenced Mission Control
  behavior are verified or an authority blocker is recorded.

## Stage 2 — Request Context Alignment

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 2.1 Confirm Request Context contract | 2.1.1 Compare Blueprint pipeline role with `config/request-context.schema.json` | Uses Request Context named in official pipeline | Core Platform only | Scope must be reviewed before implementation | Reconciles current dataclass/schema gap | Approved component contract or explicit stop |
| 2.1 Confirm Request Context contract | 2.1.2 Resolve schema/runtime fields without adding unapproved behavior | Implements only confirmed fields | Adds no Roadmap scope | Missing behavior requires authority; no inference | Accounts for conversation, parent, links, context, routing, processing, and timestamps | Field-by-field decision record |
| 2.2 Implement approved alignment | 2.2.1 Update Request Context runtime only within approved contract | Aligns official pipeline data | Core Platform progress only | Requires Stage 0 authority and reviewed change | Preserves existing Telegram factory behavior unless approved otherwise | Focused implementation diff |
| 2.2 Implement approved alignment | 2.2.2 Add schema-conformance and compatibility tests | Verifies Blueprint-facing contract | Supports later verified status | Verification distinct from approval | Adds coverage where none currently exists | Passing focused tests and boundary audit |

### Stage 2 exit gate

- Approved Request Context contract exists.
- Runtime and schema alignment is verified.
- Existing adapter integration remains verified.
- No Brain, router, or specialist behavior is introduced.

## Stage 3 — Ingestion, Storage, Metadata, and Manifest Alignment

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 3.1 Confirm ingestion contract | 3.1.1 Map Text, Image, Voice, Audio, Video, PDF, DOC/DOCX, Spreadsheet, Web link, and YouTube link handling | Covers exactly Blueprint input list | Core Platform only | No new media type beyond authority | Maps current classifier and ingestion gaps | Approved input capability matrix |
| 3.1 Confirm ingestion contract | 3.1.2 Map Receive → Store Original → Extract Metadata → Create Manifest → Register → Process → Route → Respond ownership | Covers exact Blueprint lifecycle | Does not pull Intelligence behavior into Core Platform | Stops where Process/Route ownership is undefined | Maps current function calls and missing Register step | Approved ownership/boundary record |
| 3.1 Confirm ingestion contract | 3.1.3 Implement and verify handling for every explicit Blueprint input type after the input and ownership contracts are authoritative | Implements the complete explicit input list | Core Platform only | No input may be silently deferred from completion | Extends classifier/ingestion only within confirmed boundaries | Focused implementation diff and passing capability-matrix tests |
| 3.1 Confirm ingestion contract | 3.1.4 Implement the authoritative ingestion-owned lifecycle transitions and bounded hand-offs; do not implement downstream Intelligence behavior | Implements the explicit lifecycle without inventing downstream logic | Stops before Intelligence | Undefined ownership is an authority blocker, not a deferral | Connects Stage 3 work to later Register, Event Engine, and Core stages | Sequence tests and boundary tests |
| 3.2 Align original-file storage | 3.2.1 Establish approved handling for images, voice, PDF, docs, links, and manifests paths | Uses exact Blueprint storage paths | Adds no Roadmap scope | Runtime path changes require scoped approval | Replaces image-only assumptions without touching secrets/data | Storage-path contract and migration/non-migration decision |
| 3.2 Align original-file storage | 3.2.2 Preserve “store original before process” invariant | Implements explicit Blueprint rule | Core Platform only | Invariant becomes verification gate | Extends current attachment flow safely | Tests proving original storage precedes processing |
| 3.3 Align metadata | 3.3.1 Confirm required metadata per approved media type | Supports Extract Metadata step | Core Platform only | Missing field requirements stop work | Extends current basic metadata only when authorized | Metadata contract and tests |
| 3.4 Align Document Manifest | 3.4.1 Reconcile runtime manifest with `config/ingestion-manifest.schema.json` | Implements Create Manifest step | Core Platform only | Schema change and runtime change require separate approved scope when applicable | Resolves current schema/runtime drift | Conformance matrix and decision record |
| 3.4 Align Document Manifest | 3.4.2 Verify manifest creation after storage and metadata extraction | Preserves Blueprint lifecycle order | Supports verified progress | Verification evidence required | Adds focused tests to currently uncovered modules | Passing sequence and schema tests |
| 3.5 Verify dependency boundaries | 3.5.1 Remove or explicitly approve storage coupling to Telegram/app classification | Preserves adapter/core and storage boundary intent | Adds no later-phase dependency | Architecture boundary changes require approval | Resolves `core.storage.telegram_storage` coupling risk | Dependency audit with approved disposition |

### Stage 3 exit gate

- All Blueprint input types are implemented and verified. An explicit
  Blueprint requirement may not be deferred while Core Platform is represented
  as complete.
- Original storage precedes processing.
- Runtime storage paths comply with approved Blueprint interpretation.
- Metadata and manifest contracts are verified.
- Register remains a declared next boundary; it is not silently skipped.

## Stage 4 — Asset Pipeline

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 4.1 Establish Asset Pipeline contract | 4.1.1 Identify only behavior proven by Blueprint position and approved authority | Asset Pipeline remains between Request Context and Document Manifest | Core Platform only | Blueprint ambiguity triggers stop/clarification | Does not treat historical code as contract | Approved minimal contract |
| 4.1 Establish Asset Pipeline contract | 4.1.2 Decide disposition of historical `core/pipeline/` implementation | Evaluates existing repository evidence | Does not claim completion | Requires review and approval before acceptance | Reuse/adapt/reject decision tied to commit `9d1288c` | Reviewed disposition |
| 4.2 Implement Asset Pipeline | 4.2.1 Implement only approved pipeline states and transitions | Satisfies named capability without invented scope | Core Platform only | Within approved Change Request | Uses current package organization or an explicitly approved boundary | Focused implementation diff |
| 4.2 Implement Asset Pipeline | 4.2.2 Integrate Request Context input and Document Manifest output | Preserves official pipeline order | No Intelligence routing | Integration scope explicitly approved | Connects Stages 2–3 without bypasses | Integration tests |
| 4.3 Verify Asset Pipeline | 4.3.1 Test valid, invalid, duplicate, and failure transitions defined by contract | Verifies approved Blueprint interpretation | Evidence only; no automatic Roadmap update | Verification distinct from completion claim | Restores component coverage absent from current `HEAD` | Passing focused suite and review |

### Stage 4 exit gate

- Asset Pipeline contract explicitly approved.
- Historical code disposition recorded.
- Runtime exists in current accepted branch.
- Request Context → Asset Pipeline → Document Manifest path is verified.
- README completion status is not changed until accepted evidence supports it.

## Stage 5 — PostgreSQL Registry

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 5.1 Establish Registry contract | 5.1.1 Define registry responsibility only for identity, metadata, relationships, status, and file location | Uses explicit PostgreSQL responsibility; excludes original binary | Core Platform only | Contract approval required; no ORM/design inference | Builds on current Compose asset and manifest output | Approved data responsibility contract |
| 5.1 Establish Registry contract | 5.1.2 Decide historical `core/registry/` disposition | Evaluates Blueprint Registry only | Does not claim progress automatically | Review/approval before acceptance | Reuse/adapt/reject against commit `d58c1c3` | Reviewed disposition |
| 5.2 Establish persistence boundary | 5.2.1 Approve schema/migration/transaction approach before database change | Supports Registry without changing Blueprint | Core Platform only | Database and migration authority must be explicit | Current migrations/ORM are absent; do not invent silently | Approved persistence design record |
| 5.2 Establish persistence boundary | 5.2.2 Keep original binary outside PostgreSQL | Enforces explicit storage rule | Adds no scope | Becomes verification gate | Preserves filesystem storage responsibility | Tests/audit proving metadata-only DB storage |
| 5.3 Implement Registry | 5.3.1 Implement approved register/read/update behavior required by ingestion lifecycle | Supplies Register step | Core Platform only | Within approved target list | Integrates manifest identifiers and PostgreSQL service | Focused implementation and migration evidence |
| 5.3 Implement Registry | 5.3.2 Add database isolation and failure tests | Verifies Registry contract | Supports later verified status | Verification evidence tied to exact baseline | Introduces current missing registry coverage | Passing focused integration tests |
| 5.4 Integrate Registry | 5.4.1 Connect Document Manifest → PostgreSQL Registry in lifecycle order | Preserves official pipeline | Core Platform only | Approved integration scope | Removes missing Register step | End-to-end registration evidence |

### Stage 5 exit gate

- Registry and persistence contracts approved.
- Original binaries remain outside PostgreSQL.
- Registration is implemented and verified.
- Database changes, if any, are traceable and reversible under approved
  procedure.

## Stage 6 — AIOS Event Engine

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 6.1 Establish Event Engine contract | 6.1.1 Reconcile Blueprint name, `config/event-engine.schema.json`, and Domain Foundation boundary | Implements AIOS Event Engine without confusing it with domain event exposure | Core Platform only | Contract approval required | Preserves approved DomainEvent/EventEnvelope restrictions | Approved engine contract |
| 6.1 Establish Event Engine contract | 6.1.2 Decide historical `core/event/` disposition | Evaluates Event Engine evidence only | Does not claim progress | Review/approval before acceptance | Reuse/adapt/reject against commit `c56e046` | Reviewed disposition |
| 6.2 Establish dispatch behavior | 6.2.1 Approve event registration, handler, dispatch, retry, and failure semantics | Uses configuration only where confirmed; no inferred consumer implementation | Core Platform only; excludes Brain/Specialists implementation | Explicit scope and risk approval | Resolves config/runtime absence | Behavior and failure contract |
| 6.2 Establish dispatch behavior | 6.2.2 Preserve Domain Foundation separation | Event engine consumes exposed events outside aggregate behavior | No Domain Foundation scope change | Architecture/domain authority remains intact | No dispatch/persistence added to `AggregateRoot`, `DomainEvent`, or `EventEnvelope` | Dependency and API audit |
| 6.3 Implement Event Engine | 6.3.1 Implement approved runtime and registry/dispatcher boundaries | Supplies official pipeline capability | Core Platform only | Within approved Change Request | Creates current runtime rather than schema-only claim | Focused implementation |
| 6.3 Implement Event Engine | 6.3.2 Integrate PostgreSQL Registry output with Event Engine input | Preserves official pipeline order | Core Platform only | Integration approved separately | Connects Stage 5 to Stage 6 | Integration tests |
| 6.4 Verify Event Engine | 6.4.1 Test order, duplicate handling, failures, retries, and handler isolation exactly as approved | Verifies engine contract | Supports verified status only | Exact-baseline verification | Adds missing runtime coverage | Passing suite and review |

### Stage 6 exit gate

- Event Engine contract approved.
- Domain Foundation boundary remains unchanged unless separately authorized.
- Registry → Event Engine integration is verified.
- Configuration and runtime behavior are consistent.

## Stage 7 — AIOS Core Boundary

The Blueprint names AIOS Core but does not define its behavior beyond pipeline
position. This Stage is a mandatory clarification gate.

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 7.1 Resolve AIOS Core authority | 7.1.1 Determine whether existing authority defines AIOS Core behavior | Uses named capability only | Core Platform only | Evidence review before design | Searches current and accepted historical repository | Authority finding |
| 7.1 Resolve AIOS Core authority | 7.1.2 Stop if behavior remains undefined; request Project Owner direction through the proper authority artifact | Prohibits invented architecture | Prohibits Roadmap scope invention | Requires architecture authority before implementation | Prevents speculative orchestrator/module creation | Explicit stop record or approved contract |
| 7.2 Establish Core boundary | 7.2.1 Define only the approved input from Event Engine and output toward AIOS Brain boundary | Preserves official pipeline order | Stops before Intelligence | Scope-limited approval | Identifies module/API boundary in current package organization | Approved AIOS Core contract |
| 7.3 Implement approved boundary | 7.3.1 Implement AIOS Core only after contract approval | Satisfies named capability | Core Platform only | Stage 0 plus Stage 7 approval required | Adds identifiable runtime boundary | Focused implementation and tests |
| 7.3 Implement approved boundary | 7.3.2 Provide a non-Intelligence test consumer/boundary fixture if needed | Verifies output contract without implementing Brain | Does not advance Intelligence | Test-only scope approved | Avoids specialist/router production code | Passing boundary tests |

### Stage 7 exit gate

- AIOS Core behavior is explicitly authorized.
- Runtime boundary is identifiable and verified.
- No Brain, Specialist Router, Memory, Knowledge, Planner, or specialist
  behavior is implemented.

## Stage 8 — Official Pipeline Integration

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 8.1 Assemble platform path | 8.1.1 Integrate Telegram Adapter boundary → Universal Ingestion → Request Context | Preserves official order | Core Platform integration only | Approved integration scope | Reuses current adapter without adding business logic | Passing integration test |
| 8.1 Assemble platform path | 8.1.2 Integrate Request Context → Asset Pipeline → Document Manifest | Preserves official order | Core Platform only | Same controls | Uses verified Stage 2–4 components | Passing integration test |
| 8.1 Assemble platform path | 8.1.3 Integrate Document Manifest → PostgreSQL Registry → Event Engine | Preserves official order | Core Platform only | Same controls | Uses verified Stage 5–6 components | Passing integration test |
| 8.1 Assemble platform path | 8.1.4 Integrate Event Engine → AIOS Core → downstream boundary | Stops at approved AIOS Brain boundary | Does not implement Intelligence | Same controls | Uses verified Stage 7 contract | Passing boundary test |
| 8.2 Verify lifecycle | 8.2.1 Verify Receive → Store Original → Extract Metadata → Create Manifest → Register → Process → Route → Respond ownership and sequence | Tests exact Blueprint lifecycle | Core Platform only; downstream behavior mocked/bounded | Verification tied to exact baseline | Detects bypasses and ordering failures | End-to-end lifecycle evidence |
| 8.3 Verify dependency direction | 8.3.1 Audit adapters, ingestion, storage, Core, domain, and downstream imports | Enforces Blueprint dependency direction | Prevents later-phase leakage | Architecture review required | Extends current domain dependency audits platform-wide | Passing dependency audit |
| 8.4 Verify failure behavior | 8.4.1 Test storage, metadata, manifest, registry, dispatch, and Core-boundary failures | Verifies approved pipeline resilience only | Adds no new capability | Risk-based verification | Demonstrates atomicity/traceability across components | Failure matrix and passing tests |

### Stage 8 exit gate

- Official pipeline order is verified end to end through AIOS Core.
- No later-phase implementation is present.
- Dependency audit passes.
- Failure cases preserve approved storage, registry, and event invariants.

## Stage 9 — Operational Alignment

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 9.1 Confirm service contract | 9.1.1 Confirm the implementation contract for the Blueprint-required `aios.service` without treating the absent artifact or README claim as completion | Uses explicit Blueprint service requirement | Supporting Core Platform operational requirement | Deployment/runtime authority required | Resolves missing unit versus README claim | Authoritative service contract |
| 9.1 Confirm service contract | 9.1.2 Approve unit, runtime user, environment, restart, and single-polling policy before change | Satisfies reboot, single instance, systemctl/journalctl requirements | Core Platform operational work only | Deployment/runtime authority required | Current service artifact is absent | Approved service contract |
| 9.2 Implement service alignment | 9.2.1 Add or reconcile `aios.service` after Stage 9.1 establishes its authoritative contract | Implements explicit Blueprint requirement | No scope expansion | Controlled implementation and deployment approval | Resolves current missing artifact | Reviewed service artifact |
| 9.2 Implement service alignment | 9.2.2 Verify reboot activation, one Telegram polling instance, and monitoring | Tests exact Blueprint requirements | Supports verification only | Runtime verification authority required | Produces operational rather than README-only evidence | Operational verification record |
| 9.2 Implement service alignment | 9.2.3 Establish the Blueprint-required `/opt/aios-src` source and `/opt/aios` runtime deployment separation | Implements explicit source/runtime requirement | Core Platform deployment support only | Deployment authority required; no runtime mutation before approval | Reconciles repository source with the required runtime layout | Deployment procedure, reviewed configuration, and runtime path verification |
| 9.2 Implement service alignment | 9.2.4 Verify that secrets, database data, logs, backups, and original business files are excluded from Git and remain in approved runtime locations | Enforces explicit Blueprint exclusions | No Roadmap scope addition | Security and repository verification evidence | Audits tracked files and runtime configuration without exposing secrets | Repository audit and documented verification output |
| 9.3 Reconcile operational documentation | 9.3.1 Correct capability claims only after accepted verification | Keeps docs consistent with Blueprint reality | Roadmap status changes remain separate | Documentation does not grant implementation/release authority | Reconciles README/CHANGELOG only if separately approved | Reviewed documentation evidence |

### Stage 9 exit gate

- The service contract is authoritative and the required service artifact
  exists.
- All three Blueprint service requirements are verified.
- Source/runtime separation is verified.
- No runtime secrets, database data, logs, backups, or original business files
  enter Git.

## Stage 10 — Completion, Verification, Release, and Closure

| Main Step | Sub Step | Blueprint compliance | Roadmap compliance | Governance compliance | Repository compliance | Required evidence |
|---|---|---|---|---|---|---|
| 10.1 Completion review | 10.1.1 Trace every approved Core Platform requirement to implementation and tests | Confirms Blueprint coverage | Confirms declared milestone scope only | Review is not approval | Exact file/test evidence | Requirements traceability matrix |
| 10.1 Completion review | 10.1.2 Record every excluded item and confirm that no Included Scope requirement is deferred | Prevents hidden Blueprint omissions | Prevents scope manipulation | Included requirements cannot be waived by this plan | Prevents missing work from being called complete | Reviewed exclusion list and zero-deferral confirmation |
| 10.2 Verification | 10.2.1 Run full unit, integration, schema, dependency, database, and operational suites | Verifies official pipeline and boundaries | Required before Roadmap status update | Exact baseline and declared scope recorded | Includes Domain Foundation regression suite | Verification report tied to commit |
| 10.2 Verification | 10.2.2 Perform architecture and generated-artifact audit | Confirms no later-phase leakage | Confirms no scope expansion | Independent review evidence | Confirms clean tracked tree and no secrets/runtime data | Audit report |
| 10.3 Milestone decision | 10.3.1 Request Project Owner completion and verification decision | Does not change Blueprint | Roadmap status remains unchanged until approved process permits update | Separates evidence from approval | Uses exact accepted baseline | Explicit milestone decision |
| 10.4 Release decision | 10.4.1 If release is requested, prepare scoped Release Review for exact baseline | Release covers approved Blueprint scope only | Release does not change Roadmap automatically | Follows approved release procedure; review is not approval | Records branch, commit, tests, findings, and outcome | Release Review draft |
| 10.4 Release decision | 10.4.2 Obtain explicit Project Owner release approval | No architecture effect | No automatic milestone effect | Required release authority | Accepts exact baseline only | Approved Release Review |
| 10.5 Version decision | 10.5.1 Keep `VERSION` unchanged unless a separate approval names an exact new value | No Blueprint-derived version inference | No Roadmap-derived version inference | Version change separately authorized | Current authority remains `0.1.0-alpha` until accepted edit | Version decision record |
| 10.6 Historical closure | 10.6.1 Record accepted changes, verification, release decision, documentation, and historical references | Preserves architecture traceability | Preserves roadmap traceability | Maintains auditable history | Links current code to reviewed evidence | Accepted closure record |

### Stage 10 exit gate

Core Platform may be represented as completed only when:

- every approved scope item is implemented;
- all verification gates pass on one exact accepted baseline;
- exclusions are confirmed and no Included Scope requirement is deferred;
- Project Owner completion approval is recorded;
- any Roadmap status update follows confirmed Roadmap authority;
- any release has separate explicit approval;
- any version change has separate exact-value approval;
- repository history remains auditable.

## Stage Sequence

```text
Stage 0  Authority and Baseline Gate
   ↓
Stage 1  Current Baseline Reconciliation
   ↓
Stage 2  Request Context Alignment
   ↓
Stage 3  Ingestion / Storage / Metadata / Manifest Alignment
   ↓
Stage 4  Asset Pipeline
   ↓
Stage 5  PostgreSQL Registry
   ↓
Stage 6  AIOS Event Engine
   ↓
Stage 7  AIOS Core Boundary
   ↓
Stage 8  Official Pipeline Integration
   ↓
Stage 9  Operational Alignment
   ↓
Stage 10 Completion / Verification / Release / Closure
```

Stages are sequential because each downstream capability consumes the verified
output or contract of the preceding stage. Parallel work is permitted only
when an approved working procedure proves that it cannot bypass a dependency,
authority, review, or verification gate.

## Dependencies

- Stage 0 is a hard authority prerequisite for every implementation step.
- Stage 1 fixes the accepted implementation and verification baseline before any component change.
- Stage 2 establishes the Request Context consumed by Stage 4.
- Stage 3 establishes storage, metadata, and manifest prerequisites consumed by Stages 4 and 5.
- Stage 4 produces the Asset Pipeline output consumed by the Document Manifest boundary.
- Stage 5 implements registration before Stage 6 consumes registered output.
- Stage 6 implements event delivery before Stage 7 defines the AIOS Core input.
- Stage 8 integrates only components verified in Stages 2 through 7.
- Stage 9 validates the operational environment after the integrated runtime exists.
- Stage 10 follows all implementation and validation and cannot repair an earlier failed gate.

## Completion Criteria

A Sub Step is complete only when its Required evidence cell is satisfied against the exact working baseline and its parent Main Step has no failed Sub Step. A Main Step is complete only when all of its Sub Steps are complete. A Stage is complete only when every Main Step and the stated exit gate pass. Core Platform completion additionally requires every explicit Blueprint capability in Included Scope to be implemented and verified; no required capability may be hidden by an exception or deferral.

## Verification Requirements

Evidence must be created by the future authorized implementation work, not fabricated in advance. Depending on the Sub Step, acceptable evidence is a reviewed source or configuration diff, automated unit, integration, schema, or dependency test output, migration verification, runtime or operational command output, an exact-baseline audit, or an explicit authority record. Evidence must name the baseline, scope, command or review method, outcome, and unresolved exceptions. A document claim without implementation or verification evidence does not satisfy a runtime completion condition.

## Traceability

Every Stage, Main Step, and included Sub Step inherits the evidence mapped below in addition to the row-specific compliance and Required evidence cells.

| Plan items | Supporting repository evidence |
|---|---|
| 0.1.1–0.4.3 | `CORE_PLATFORM_AUTHORITY_DECISION.md`; `CORE_PLATFORM_MILESTONE_OPENING.md`; active Blueprint and Roadmap; GD-001 through GD-007; `EF03_CORE_PLATFORM_ROADMAP_ALIGNMENT.md:212-237`; `EF04_CORE_PLATFORM_GOVERNANCE_ALIGNMENT.md:20-158`, `254-325` |
| 1.1.1–1.4.2 | `EF01_CORE_PLATFORM_REPOSITORY_AUDIT.md:19-109`, `180-339`; `README.md`; `core/`; `config/`; `tests/` |
| 2.1.1–2.2.2 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:27-45`; `config/request-context.schema.json`; `core/app/request_context.py`; EF-02 Request Context finding |
| 3.1.1–3.5.1 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:99-145`, `215-227`; `core/ingestion/`; `core/storage/`; `config/ingestion-manifest.schema.json`; EF-02 ingestion, storage, and manifest findings |
| 4.1.1–4.3.1 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:35-39`; EF-01 historical commit `9d1288c`; EF-02 Asset Pipeline finding |
| 5.1.1–5.4.1 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:39-43`, `134-145`; `docker/postgres/compose.yml`; EF-01 historical commit `d58c1c3`; EF-02 Registry finding |
| 6.1.1–6.4.1 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:41-45`; `config/event-engine.schema.json`; Domain Foundation sections 7–8; EF-01 historical commit `c56e046`; EF-02 Event Engine finding |
| 7.1.1–7.3.2 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:43-47`; EF-02 AIOS Core missing and unverifiable finding |
| 8.1.1–8.4.1 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:27-53`, `116-132`, `215-227`; verified outputs required from Stages 2–7 |
| 9.1.1–9.3.1 | Blueprint `e6ac77a3b:docs/AIOS_ARCHITECTURE_v1.md:147-169`; `README.md`; `CHANGELOG.md`; EF-01 and EF-02 systemd findings |
| 10.1.1–10.6.1 | Active `docs/AIOS_Roadmap_Frozen.md`; `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md`; Active GD-004 through GD-007 |

## Total Counts

- Stages: **11**
- Main Steps: **42**
- Sub Steps: **79**

The counts include Stage 0 through Stage 10. Exit gates, narrative rules, and the Stage Sequence are not counted as Main Steps or Sub Steps.

## Freeze Preconditions

This draft is not eligible to be frozen until:

1. EF-06 has no unresolved CRITICAL or MAJOR finding.
2. The exact Blueprint and Roadmap authority applicable to Core Platform is established in current accepted repository evidence.
3. Required Core Platform architecture contracts are sequenced as the earliest
   evidence-supported deliverables and must be completed before dependent
   implementation.
4. Foundation readiness and the Core Platform boundary can be determined without conflict.
5. Every Stage, Main Step, and Sub Step remains traceable, sequential, specific, and verifiable.
6. EF-07 independently decides whether to freeze the plan.

Freeze does not itself authorize implementation unless the explicit Project Owner record required by repository authority also grants that scope.

## Global Stop Conditions

Stop execution immediately when any of the following occurs:

1. Project Owner implementation authority is absent, expired, superseded, or
   exceeded.
2. Blueprint or Roadmap authority is unresolved.
3. A required capability contract is not found in approved repository
   evidence.
4. Proposed work would enter Intelligence, Business Capability, Interfaces, or
   External Integrations.
5. Proposed work would modify Blueprint, Roadmap, governance, Domain Foundation
   authority, or `VERSION` without separate explicit approval.
6. Historical branch code is being treated as current implementation without
   review and acceptance.
7. A stage fails its verification or dependency-boundary gate.
8. Scope changes beyond the approved Change Request.
9. Secrets, database data, logs, backups, or original business files would
   enter Git.
10. A completion, release, milestone, or version claim lacks its separate
    required evidence and approval.

## Plan Acceptance Criteria

This draft is ready to request review when:

- every plan item maps to Blueprint, Roadmap, Governance, and Repository;
- no later-phase capability is included;
- no unspecified technical design is asserted as authority;
- all authority gaps are represented as gates, not assumptions;
- all historical code is treated as evidence, not current implementation;
- completion, verification, release, and version remain separate decisions.

This draft becomes executable only after explicit Project Owner approval that
identifies:

- this document and exact revision;
- the accepted Blueprint and Roadmap baselines;
- the applicable governance process;
- the approved Core Platform milestone scope;
- the repository baseline and target branch;
- authorized implementation targets and exclusions.

## Conclusion

This plan provides a staged path from the current repository to the Core
Platform path named by the frozen Blueprint. It starts with authority and
baseline reconciliation, aligns partial current assets, introduces missing
capabilities in Blueprint order, verifies the end-to-end platform boundary, and
separates completion, release, Roadmap status, and version decisions.

The plan is **APPROVED FOR FREEZE**, **ELIGIBLE FOR EF-07**, and **NOT YET
FROZEN**. It remains **NOT YET AUTHORIZED FOR IMPLEMENTATION**. No
implementation may begin before EF-07 successfully freezes the plan and every
applicable Stage 0 implementation condition is satisfied.

EF-06 changed only permitted documentation. It performed no source, test,
database, deployment, runtime, or implementation change.
