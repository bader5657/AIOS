# AIOS Authority Hierarchy

| Field | Value |
|---|---|
| Document | `AIOS_AUTHORITY_HIERARCHY.md` |
| Status | **PUBLISHED** |
| Activation | **Pending repository activation** |
| Document class | Architecture authority foundation |
| Approval authority | Project Owner |
| Effective authority | None until explicitly Active |

## Why This Document Is Required

AIOS has multiple documents with different subjects, scopes, lifecycle states,
and authority claims. A common rule is required to determine which document may
govern a question, how conflicts are contained, and when a document becomes or
ceases to be current authority.

Without this foundation, later architecture documents could accidentally treat
repository presence as authority, apply a document outside its scope, or expand
the Blueprint by interpretation.

## Purpose

Define the hierarchy, scope application, approval hierarchy, conflict
resolution, supersession rules, and document precedence for AIOS authority
documents while preserving the Blueprint as the highest Source of Truth.

## Scope

This document governs only how AIOS repository authority is identified,
ordered, applied, approved, and superseded.

It applies to:

- the Blueprint;
- the Frozen Roadmap;
- the Domain Foundation;
- Governance Decisions;
- Authority Decisions;
- architecture authority documents created after this document;
- ADRs; and
- descriptive, review, status, implementation, test, and historical artifacts
  when their authority must be evaluated.

## Non-Goals

This document does not:

- change, reinterpret, complete, or extend the Blueprint;
- change the Frozen Roadmap or its scope and progress;
- change the Domain Foundation or its published contracts;
- create canonical vocabulary, object flow, layers, dependencies, or domain
  behavior;
- authorize implementation, source changes, tests, release, deployment, or
  runtime behavior;
- create a database, API, schema, event payload, workflow runtime, state
  machine, persistence model, class, or code; or
- approve any later architecture document or ADR.

## Authority Source

This document is derived only from the following authority and repository
evidence:

1. `docs/AIOS_ARCHITECTURE_v1.md` — Blueprint architecture and design content.
2. `docs/AIOS_Roadmap_Frozen.md` — declares the Blueprint the Source of Truth,
   limits the Roadmap to implementation progress, and requires architecture
   changes to occur through the Blueprint.
3. `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — approved
   repository authority for its explicitly published Domain Foundation scope;
   prohibits inference from unpublished contracts and requires explicit
   Project Owner decisions for changes.
4. `docs/governance/GOVERNANCE_DECISION_001.md` — records the governance
   approval stages, Project Owner approval, and official-record effect upon
   commit.
5. `docs/governance/GOVERNANCE_DECISION_002.md` — defines artifact lifecycle,
   scope-limited Active authority, and the distinction between approval,
   publication, and activation.
6. `docs/governance/GOVERNANCE_DECISION_003.md` through
   `docs/governance/GOVERNANCE_DECISION_007.md` — active scope-specific
   governance for repository acceptance, releases, versioning, milestones, and
   managed changes.
7. `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md` — active authority
   for its declared Core Platform scope and evidence that Authority Decisions
   are scope-limited.
8. The Project Owner instruction dated 2026-08-03 initiating Architecture
   Recovery, expressly requiring the Blueprint to remain the highest Source of
   Truth and every new document to remain subordinate.

The repository location and permanent identifier for the initiating Project
Owner instruction are **UNRESOLVED**. A Project Owner-approved repository record
is required to make that instruction independently traceable from repository
history.

## Dependencies

This document depends on:

- the Blueprint for the highest architecture and design authority;
- the Frozen Roadmap for the Blueprint-over-Roadmap relationship and roadmap
  change constraints;
- Governance Decisions 001 and 002 for approval, publication, activation,
  lifecycle, and repository-authority rules;
- Governance Decisions 003 through 007 for their separate declared governance
  scopes;
- the Domain Foundation Master for its published domain-contract scope and
  non-inference rule; and
- active, explicit Authority Decisions only within their declared scopes.

This document does not depend on the Canonical Model, Pipeline Model, Layer
Architecture, or ADRs. Those documents do not yet exist as approved authority
and, if later approved, must depend on this document.

This dependency is one-way. No content, status, approval, or authority of this
document is derived from the Canonical Model, Pipeline Model, Layer
Architecture, or any ADR. Those subordinate documents therefore cannot become
a circular source of authority for this document.

## Authority Types

This section classifies the kinds of authority and non-authority artifacts used
in AIOS. It is classification only: it creates no authority, changes no
hierarchy or precedence, and does not change the Blueprint.

| Type | Purpose | Example |
|------|---------|---------|
| Architecture Authority | Menetapkan arsitektur dan aturan tingkat sistem | Blueprint |
| Domain Authority | Menetapkan kontrak dan aturan domain pada scope-nya | Domain Foundation |
| Vocabulary Authority | Menetapkan istilah dan identitas objek arsitektur | `AIOS_CANONICAL_MODEL.md` |
| Layer Authority | Menetapkan ownership, boundary, dan dependency antar layer | `AIOS_LAYER_ARCHITECTURE.md` |
| Decision Authority | Mencatat keputusan arsitektur yang telah disetujui | ADR |
| Execution Authority | Mengatur urutan implementasi dan pelaksanaan pekerjaan | Execution Plan |
| Evidence | Menyediakan bukti, audit, review, dan hasil verifikasi; bukan sumber authority | Audit Reports, Verification Reports, Consistency Matrix |
| Navigation | Membantu menemukan dokumen authority; bukan sumber authority | `AIOS_KNOWLEDGE_BASE.md` / `AIOS_AUTHORITY_INDEX.md` |

Classification rules:

- one document may have only one primary authority;
- Evidence is never authority;
- Navigation is never authority;
- a file does not acquire authority merely by being present in the repository;
- authority applies only after the governance lifecycle is complete: Draft →
  Reviewed → Approved → Published → Active; and
- if a document serves more than one function, its primary authority must be
  stated explicitly.

### Non-Goals

This section does not:

- change the hierarchy;
- change precedence;
- create a new authority;
- change the Blueprint;
- change the Roadmap;
- change the Domain Foundation; or
- change Governance Decisions.

It only classifies types of authority and non-authority artifacts.

## Document Position

This document is subordinate to the Blueprint. It is a cross-document
governance foundation for all later architecture authority documents.

The document order is:

```text
Blueprint
  ↓
AIOS Authority Hierarchy
  ↓
AIOS Canonical Model
  ↓
AIOS Pipeline Model
  ↓
AIOS Layer Architecture
  ↓
ADRs that lock decisions within the approved authority above them
```

This order establishes derivation and constraint, not implementation sequence
or permission. A lower document may constrain its own narrower scope but may
not modify, enlarge, contradict, or supersede a higher document.

Precedence and scope are separate. Higher precedence does not grant unlimited
scope: the Blueprint remains highest for architecture and system design, but it
does not thereby define every implementation detail. A lower authority applies
only to its explicit scope and only when compatible with every applicable
higher authority.

The Frozen Roadmap, Domain Foundation, Governance Decisions, and Authority
Decisions retain authority only for their own declared subjects and Active
scope. They are not inserted into the derivation chain above as interchangeable
architecture definitions.

## Rules

### 1. Authority Order

1. The Blueprint is the highest Source of Truth for AIOS architecture and
   system design.
2. No subordinate artifact may amend the Blueprint by interpretation,
   implication, aggregation, implementation evidence, or narrower authority.
3. Below the Blueprint, authority is selected by declared subject and scope;
   file type or recency alone does not create precedence.
4. This document governs authority evaluation only after it becomes Published
   and Active. Its Reviewed and Approved state alone grants no effective
   authority.
5. Later architecture documents and ADRs are subordinate to every applicable
   higher authority and may govern only their explicitly approved scope.

### 2. Document Precedence

For a specific question, apply documents in this order:

1. apply the Blueprint;
2. exclude any interpretation that is not traceable to explicit authority;
3. identify all Approved, Published, and Active documents whose declared scope
   covers the question;
4. apply the authority that is most specific to the question, provided it does
   not conflict with the Blueprint or another applicable higher document;
5. apply lifecycle and repository-evidence rules from active Governance
   Decisions without allowing those rules to create substantive architecture,
   roadmap, domain, or implementation authority; and
6. if authority remains absent, ambiguous, or conflicting, record
   **UNRESOLVED** and stop the affected decision.

Specificity resolves overlap only among compatible, Active authorities. It
does not allow a narrower document to override the Blueprint or expand a
higher document.

### 3. Scope Authority

- The Blueprint governs AIOS architecture and system design.
- The Frozen Roadmap governs only authorized implementation phase order, scope,
  and verified progress. It does not change architecture.
- The Domain Foundation Master governs only its explicitly published domain
  contracts. Content marked `Not Yet Published` is non-authoritative.
- Governance Decisions govern only their declared governance subjects. They do
  not create substantive architecture or implementation authority unless an
  explicit higher authority separately grants that scope.
- Authority Decisions govern only the exact decisions, boundary, duration, and
  scope they explicitly activate or authorize.
- The Canonical Model, when Active, may define canonical object identity and
  vocabulary only.
- The Pipeline Model, when Active, may define canonical object flow,
  transformation, inputs, outputs, and lifecycle transitions only.
- The Layer Architecture, when Active, may define layer ownership,
  responsibility, dependencies, communication, and boundaries only, using the
  approved Canonical and Pipeline Models.
- ADRs may lock only an already authorized decision within their declared
  scope. An ADR may not manufacture missing authority.
- Source code, tests, reviews, README, CHANGELOG, journals, status reports,
  branches, pull requests, commits, and runtime state do not become
  architecture authority merely because they exist or are accepted.

The authority-to-scope mapping is therefore explicit:

| Authority | Scope |
|---|---|
| Blueprint | AIOS architecture and system design |
| Frozen Roadmap | Authorized implementation phase order, execution scope, and verified progress |
| Domain Foundation | Published domain contracts and domain rules within its declared scope |
| Canonical Model, when Active | Canonical vocabulary and architectural object identity |
| Layer Architecture, when Active | Layer ownership, responsibility, boundaries, and dependency direction |
| ADR, when Active | The specific approved architecture decision identified by that ADR |

### 4. Approval Hierarchy

1. The Project Owner is the approval authority.
2. Authors, contributors, reviewers, implementers, testers, documenters,
   custodians, branch owners, and PR participants gain no independent approval
   authority from those roles.
3. Review is not approval. Approval is not publication. Publication is not
   activation.
4. A new authority document becomes current authority only after explicit
   Project Owner approval, acceptance into repository history, and explicit
   activation for a declared scope in accordance with GD-002.
5. Delegated approval is valid only when an explicit Project Owner authority
   identifies the delegate, scope, limits, and applicable decision. No general
   delegated architecture-approval role is currently published.

General delegation procedure, expiry, revocation, and emergency approval are
**UNRESOLVED**. They require an explicit Project Owner governance decision.

### 5. Conflict Resolution

When two statements appear to conflict:

1. confirm that both artifacts are Approved, Published, and Active;
2. compare their declared subjects and scopes;
3. preserve the Blueprint without reinterpretation;
4. disregard a statement applied outside its declared scope;
5. prefer an explicitly narrower compatible authority only for its narrower
   scope;
6. do not use dates, filenames, numbering, commits, branches, reviews, or
   implementation state as an implied override; and
7. when the conflict cannot be resolved by explicit scope and precedence,
   mark the matter **UNRESOLVED** and require a Project Owner decision.

Conflict does not create authority. Silence does not create authority. Missing
authority does not permit inference.

### 6. Conflict Resolution Examples

These examples apply the rules above; they do not create new authority:

- **Blueprint vs Layer Architecture:** for an architecture statement covered
  by both, the Blueprint wins. The Layer Architecture must be corrected or the
  conflict marked **UNRESOLVED**; it cannot amend the Blueprint.
- **Domain Foundation vs ADR:** within the Domain Foundation's published domain
  scope, the Domain Foundation wins. The ADR may govern only a compatible,
  narrower decision and cannot rewrite the domain contract.
- **Blueprint vs Roadmap:** for architecture or system design, the Blueprint
  wins. The Roadmap governs only phase order, execution scope, and verified
  progress.
- **Evidence vs an Active authority:** the Active authority governs. Evidence
  may demonstrate a discrepancy but cannot override or supersede authority.

### 7. Core Platform Wording Validation

`docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md` activates the Blueprint
for Core Platform “subject to the Domain Foundation Master and approved
governance hierarchy.” This wording does not change precedence. Its own table
makes the Roadmap subject to the Blueprint, while the Domain Foundation and
Governance Decisions expressly exclude changes to the Blueprint. Applied within
each document's declared scope, these statements are compatible and preserve
the Blueprint as the highest architecture Source of Truth.

### 8. Supersession Rules

1. Supersession must be explicit; it must never be inferred from a newer date,
   version number, filename, merge, commit, or implementation change.
2. A superseding authority must identify the affected document, exact scope,
   replacement authority, effective status, and Project Owner approval.
3. A subordinate document cannot supersede the Blueprint or another higher
   authority.
4. Architecture changes require a Blueprint change approved by the Project
   Owner; they cannot be performed through the Roadmap, an ADR, implementation,
   or this document.
5. Roadmap changes must comply with the Blueprint and the Roadmap's own update
   rules. This document does not authorize any Roadmap change.
6. Domain Foundation changes require an explicit Project Owner decision and
   cannot modify the Blueprint or Frozen Roadmap.
7. A superseded document remains traceable in accepted repository history and
   must not regain Active status automatically.
8. Supersession must follow GD-002 lifecycle treatment and GD-007 historical
   preservation rules.

For example, `ADR-011` may explicitly supersede `ADR-002` only when both cover
the identified decision scope, the replacement and effective status are
explicit, and Project Owner approval is recorded. An ADR can never supersede
the Blueprint, the Domain Foundation in its published domain scope, or another
applicable higher authority.

A repository-wide supersession record format and the authority to restore a
superseded document beyond explicit Project Owner action are **UNRESOLVED**.
They require a Project Owner governance decision.

### 9. Rules for Missing Authority

- Use the exact marker **UNRESOLVED**.
- State the missing authority and the decision that cannot proceed.
- Do not fill the gap with common practice, implementation evidence, historical
  content, or architectural preference.
- Do not proceed with dependent authority or implementation until the required
  authority is explicitly approved, published, and active.

## Out of Scope

The following remain outside this document:

- canonical object definitions;
- domain models and domain decisions;
- object flow and transformations;
- layer design, ownership, or dependency direction;
- workflow orchestration or runtime behavior;
- implementation plans or technical designs;
- modifications to the Blueprint, Frozen Roadmap, Domain Foundation,
  Governance Decisions, or Authority Decisions; and
- approval or activation of any subsequent document.

## Traceability

| Rule group | Authority or evidence |
|---|---|
| Blueprint is highest; Roadmap is subordinate | `docs/AIOS_Roadmap_Frozen.md`, preamble and Update Rules 1, 2, and 5; Project Owner instruction dated 2026-08-03 |
| No scope expansion or invented authority | `docs/AIOS_Roadmap_Frozen.md`, Update Rule 4; Domain Foundation Master sections 11, 13, and 14; Project Owner instruction dated 2026-08-03 |
| Project Owner approval | GD-001 Approval Record; GD-002 Repository Lifecycle; Domain Foundation Master Document Status |
| Approval, publication, and activation are distinct | GD-001 Repository Impact; GD-002 Repository Lifecycle, Transition Rules, and Governance Rules |
| Scope-limited authority | GD-002 Governance Rules 4 and 6; GD-003 through GD-007 Authority, Scope, and Conflict Resolution sections |
| Branch, PR, merge, or presence does not create authority | GD-002 Governance Rules 2–5; GD-003 Rules 1–6 |
| Supersession preserves history | GD-002 Historical, Deprecated, and Archived lifecycle treatment; GD-007 Rules 8, 10–12 |
| Frozen Roadmap cannot be expanded by status reporting | `docs/AIOS_Roadmap_Frozen.md`, Update Rules 3 and 4; GD-006 Rules 7 and 10 |
| Domain Foundation applies only to published scope | Domain Foundation Master sections 1, 11, 13, and 14 |
| Core Platform authority is scope-limited | `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md`, Decisions and Limits |

Every normative rule in this document must remain traceable to a row above or
to a later explicit Project Owner-approved authority. A rule without such a
source is **UNRESOLVED** and must not be activated.

## Open Questions

1. **UNRESOLVED — Initiating instruction record.** Which repository artifact
   will permanently record the Project Owner's 2026-08-03 Architecture Recovery
   instruction?
2. **UNRESOLVED — Delegation.** Is any role allowed to approve architecture
   authority on behalf of the Project Owner? A scoped Project Owner governance
   decision is required.
3. **UNRESOLVED — Supersession record.** What mandatory repository format must
   record supersession? A Project Owner governance decision is required.
4. **UNRESOLVED — Same-scope conflict.** Is any resolution body or escalation
   path authorized beyond the Project Owner? A Project Owner governance
   decision is required.

These questions do not invalidate the completed review or approval of this
document, but their unresolved subjects remain non-authoritative.

## Future Decisions

The following may be decided only through later explicit Project Owner
authority and are not decided here:

- publication and activation of this document after acceptance into repository
  history;
- permanent recording of the Architecture Recovery instruction;
- delegated approval, emergency authority, or an authority-review body;
- a mandatory supersession-record format;
- restoration rules for deprecated, historical, or superseded authority; and
- any authority gap discovered while preparing later architecture documents.

No Future Decision listed here is authorized merely by being listed.

## Final Review and Approval Record

Final architecture review completed on 2026-08-03 against the Blueprint,
Frozen Roadmap, Domain Foundation, Governance Decisions 001–007, and the Core
Platform Authority Decision.

The review confirmed:

- no circular authority: this document stands independently of the Canonical
  Model, Pipeline Model, Layer Architecture, and ADRs;
- every authority class addressed by this document has an explicit scope;
- precedence is separate from scope;
- conflict-resolution examples preserve the Blueprint and applicable
  scope-specific authorities;
- supersession is explicit, scope-limited, history-preserving, and unavailable
  to subordinate documents against higher authority;
- the hierarchy and precedence chain are unchanged;
- Authority Types is classification only and creates no authority; and
- no conflict was found with the Blueprint or Governance Decisions.

The Project Owner instruction dated 2026-08-03 authorizes this completed review
and approval. The document is therefore **Reviewed** and **Approved**.

**Status:** Published

**Activation:** Pending repository activation

Publication records the completed review and approval in accepted repository
history. Under GD-002, publication does not itself activate this document; it
remains non-authoritative until activation is explicitly recorded.

