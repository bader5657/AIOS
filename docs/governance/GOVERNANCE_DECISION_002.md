# AIOS Governance Decision 002

Status:
DRAFT

Decision ID:
GD-002

Authority:
Project Owner

## Purpose

This decision defines the governance lifecycle of repository artifacts from creation through archival. It defines lifecycle states, ownership constraints, valid transitions, and repository expectations. It does not grant implementation authority.

## Scope

This decision applies only to artifacts recorded in the AIOS repository and to their treatment as repository governance records. It governs artifact status; it does not govern software architecture, delivery planning, milestones, release approval, or implementation content.

## Background

The repository contains artifacts with explicit but non-uniform status language:

- Governance Decision 001 is `APPROVED`, was approved for publication, and becomes the official repository record upon commit. [E1]
- The Domain Foundation Master is an `Approved repository authority`, distinguishes published from not-yet-published content, and states that unpublished content is not implementation authority. [E2]
- Release Review v0.4 is `Approved`, identifies `main`, relies on accepted Git history, and distinguishes current repository authority from accepted documentation history. [E3]
- The six later governance skeletons, including the original skeleton for this decision, were committed with `DRAFT` status. [E4]
- The historical Roadmap identifies itself as `Frozen`; the historical Project Status identifies the architecture and roadmap as `Frozen`; and the historical Blueprint was added to repository history. [E5] [E6] [E7]

A complete lifecycle shared by all artifact classes was not previously defined. Not defined in repository.

## Decision

The repository artifact lifecycle and classification rules in this decision are adopted as the governance model for evaluating artifact state. These rules define governance treatment only. They do not change the substantive authority or content of any artifact.

## Repository Lifecycle

An artifact state is determined by explicit status recorded in the artifact or by an accepted repository record that identifies that status. Mere file existence does not assign a state other than Draft.

“Owner” means the person allowed to maintain the artifact in that stage. Approval authority remains with the Project Owner, consistent with Governance Decision 001 and the Domain Foundation Master. [E1] [E2] A contributor may act only within Project Owner authorization and does not acquire independent approval authority.

| Stage | Meaning | Allowed owner | Allowed transition | Repository expectation |
|---|---|---|---|---|
| Draft | Incomplete working content with no repository authority. | Project Owner or authorized artifact author. | Proposed. | Must state `DRAFT`; may exist in a branch or accepted history; must not be cited as active authority. |
| Proposed | Complete enough to request formal review, but not approved. | Project Owner or authorized artifact author. | Reviewed. | Must identify itself as proposed and retain reviewable evidence; it has no active authority. |
| Reviewed | Review is complete and the artifact awaits an approval decision. Review is not approval. | Project Owner or authorized reviewer. | Approved. | Must record the review outcome and evidence; it remains non-authoritative until approval. |
| Approved | The Project Owner has explicitly accepted the artifact. Approval alone does not prove publication. | Project Owner. | Published. | Must contain or reference an approval record in accepted repository history. Governance Decision 001 evidences explicit Project Owner approval practice. [E1] |
| Published | The approved artifact is present in accepted repository history and is available as an official repository record. | Project Owner or authorized repository custodian. | Active, Historical, or Deprecated. | Must be merged or committed into accepted repository history. Governance Decision 001 ties official-record status to commit. [E1] |
| Active | The published artifact currently governs, describes, verifies, or records its declared repository scope. | Project Owner or authorized repository custodian. | Historical or Deprecated. | Must have explicit active status or an accepted repository record establishing current authority. The Domain Foundation Master is explicitly designated repository authority. [E2] |
| Historical | Retained as evidence of an earlier repository state and not current authority. | Project Owner or authorized repository custodian. | Archived. | Must remain traceable in accepted repository history and must not be treated as Active automatically. Release Review v0.4 separates accepted documentation history from current authority. [E3] |
| Deprecated | Available, but its use as current guidance or authority has been withdrawn or superseded. | Project Owner or authorized repository custodian. | Historical or Archived. | Must identify the deprecation and, when proven, its replacement. Existing repository-wide deprecation procedure: Not defined in repository. |
| Archived | Retained only for long-term record and outside the active working set. | Project Owner or authorized repository custodian. | None. | Must remain traceable and must not be used as current authority. Existing archive location or mechanism: Not defined in repository. |

`Frozen`, `IN PROGRESS`, and `Not Yet Published` occur in repository evidence but are not additional lifecycle stages. [E2] [E5] [E6]

- `Frozen` is a content-change constraint. A frozen artifact still requires an explicit lifecycle state; frozen status alone does not prove that it is Active.
- `IN PROGRESS` maps to Draft unless an accepted repository record explicitly establishes another lifecycle state.
- `Not Yet Published` is non-authoritative and maps to Draft or Proposed according to its explicit review status. The Domain Foundation Master expressly states that such content is not implementation authority. [E2]

## Artifact Classification

Lifecycle requirements vary by artifact function, but no classification bypasses the transition rules.

| Artifact | Classification and lifecycle treatment | Repository evidence |
|---|---|---|
| Blueprint | Architecture authority artifact. Only an explicitly Approved, Published, and Active Blueprint may serve as current architecture authority. No Blueprint is present in the current tree; an earlier Blueprint remains in Git history. Its current lifecycle state is not established by a current artifact. Not defined in repository. | Commit `bbbc601` adds `docs/AIOS_ARCHITECTURE_v1.md`; the historical Roadmap names it as source of truth. [E5] [E7] |
| Roadmap | Planning authority artifact. Only an explicitly Approved, Published, and Active Roadmap may serve as current planning authority. A frozen Roadmap exists in accepted history but not the current tree. Its current lifecycle state is not established by a current artifact. Not defined in repository. | Release Review v0.4 refers to frozen Roadmap authority in accepted documentation history; commit `da9d692` records it. [E3] [E5] |
| Domain Foundation Master | Architecture/domain authority artifact. Published sections are Active within the declared scope; `Not Yet Published` sections are non-authoritative. | The current document states `Approved repository authority`, identifies published scope, and rejects implementation authority for unpublished material. [E2] |
| Release Review | Review and approval record. It becomes Published when accepted into history. Its findings record the reviewed baseline; this decision does not approve a release or make a review perpetually Active. | Release Review v0.4 records its baseline, branch, authority chain, review result, and release approval. [E3] |
| `VERSION` | Release-identifier artifact. Its accepted content identifies repository version, but lifecycle labels for the file are absent. Not defined in repository. Changes require accepted repository history and cannot be inferred from another artifact’s lifecycle. | Current `VERSION` contains `0.1.0-alpha`; README and CHANGELOG repeat it. [E8] [E9] [E10] |
| Source Code | Implementation artifact. Draft through Reviewed apply to proposed changes; accepted code may be Published and Active for the baseline. Per-file lifecycle metadata and ownership: Not defined in repository. This decision grants no implementation authority. | The Release Review identifies a source baseline and checks implementation against published authority. [E3] |
| Tests | Verification artifact. Draft through Reviewed apply to proposed changes; accepted tests may be Published and Active for the baseline. Per-file lifecycle metadata and ownership: Not defined in repository. This decision grants no test-change authority. | The Release Review records test results and treats tests as baseline evidence. [E3] |
| Governance Decision | Governance record. It has no authority while Draft, Proposed, or Reviewed. It becomes an official Published record only after explicit approval and acceptance into history; it is Active only for its declared scope. | Governance Decision 001 records approval, publication, and official-record effect upon commit. Decisions 002–007 entered history as Draft skeletons. [E1] [E4] |
| `README` | Descriptive repository entry artifact. Accepted content may be Published and Active as orientation, but it does not become architecture, roadmap, release, or implementation authority merely by existing. Explicit lifecycle metadata: Not defined in repository. | Current README states project name, version, capabilities, structure, and status. [E9] |
| `CHANGELOG` | Historical release-summary artifact. Accepted entries are Published records; they become Historical when superseded as current release context but remain in history. Explicit changelog lifecycle policy: Not defined in repository. | Current CHANGELOG records `0.1.0-alpha` and stated additions. [E10] |
| Engineering Journal | Ongoing engineering record. `IN PROGRESS` content is Draft unless another state is explicitly approved; completed entries may become Published historical evidence. It is not architecture or implementation authority by default. | The current journal states `IN PROGRESS` and requires major infrastructure changes to be recorded. [E11] |
| Project Status | Status-report artifact. A snapshot may be Published for its recorded point and becomes Historical when superseded. No Project Status is in the current tree; an earlier snapshot remains in history and is Historical, not Active. | Commit `e6ac77a` contains `PROJECT_STATUS.md` dated 2026-07-23. [E6] |

## Transition Rules

The ordinary valid lifecycle is:

```text
Draft → Proposed → Reviewed → Approved → Published → Active → Historical → Archived
```

The following alternate forward transitions are valid:

```text
Published → Historical
Published → Deprecated
Active → Deprecated
Deprecated → Historical
Deprecated → Archived
```

Rules:

1. A transition is valid only when the destination is listed for the current stage in the Repository Lifecycle table.
2. No stage may be skipped except by an alternate forward transition expressly listed above.
3. No backward transition is valid unless the Project Owner explicitly approves it in an accepted repository record.
4. An approved backward transition does not erase history or restore authority automatically; the artifact must again satisfy every expectation for its destination state.
5. Archived is terminal. A replacement for an Archived artifact begins a new lifecycle as Draft.
6. Status changes must be explicit. Modification, branch creation, pull-request creation, merge, or file presence alone does not imply a transition.

An existing repository-wide process for recording backward-transition approvals was not previously specified. Not defined in repository.

## Governance Rules

1. Historical documents never become Active automatically.
2. Branch documents never become Active merely because they exist.
3. Pull-request documents never become repository authority until merged into accepted repository history.
4. Active authority must exist in accepted repository history and be explicitly identifiable as current authority for its scope.
5. Merge or commit is necessary for Published status but is insufficient for Approved or Active status without the required explicit records.
6. A lifecycle state applies only to the scope declared by the artifact.
7. Conflicting or missing status evidence does not create authority. The artifact remains non-Active until the Project Owner records a valid transition.

Release Review v0.4 distinguishes accepted history from current authority. [E3] Governance Decision 001 makes official-record status effective upon commit. [E1] A repository-wide pull-request authority rule was not previously stated. Not defined in repository.

## Evidence

- **[E1]** `docs/governance/GOVERNANCE_DECISION_001.md` — approved status, governance process, Project Owner approval, publication, and official record upon commit.
- **[E2]** `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — approved repository authority, Project Owner authority, published scope, and unpublished restrictions.
- **[E3]** `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` — approved review, baseline, `main`, accepted authority chain, current authority, and accepted documentation history.
- **[E4]** Commit `7eec0cc` — creation of Governance Decision 002–007 skeletons with `DRAFT` status.
- **[E5]** Commit `da9d692`, `docs/AIOS_Roadmap_Frozen.md` — frozen Roadmap status, source-of-truth statement, update rules, and revision history.
- **[E6]** Commit `e6ac77a`, `PROJECT_STATUS.md` — dated status snapshot with frozen architecture and roadmap fields.
- **[E7]** Commit `bbbc601`, `docs/AIOS_ARCHITECTURE_v1.md` — historical Blueprint publication.
- **[E8]** `VERSION` — current release identifier.
- **[E9]** `README.md` — current description, version, capabilities, structure, and project-status statements.
- **[E10]** `CHANGELOG.md` — current recorded release entry.
- **[E11]** `docs/engineering-journal.md` — current journal status and recording rule.

## Affected Artifacts

This decision directly changes only `docs/governance/GOVERNANCE_DECISION_002.md`. It classifies listed artifacts for governance purposes but does not change their content, status, authority, or implementation.

## Out of Scope

This decision does not:

- create a milestone;
- approve a release;
- modify architecture;
- modify the Blueprint;
- modify the Roadmap;
- modify implementation;
- modify source code or tests;
- change `VERSION`;
- create implementation authority;
- approve any other governance decision; or
- override Governance Decision 001.

## Implementation Impact

None. This documentation-only decision authorizes no source, test, architecture, release, version, roadmap, milestone, deployment, or other implementation change.

## Approval

This document remains `DRAFT`. It does not record approval of Governance Decision 002. Approval beyond the authority already identified in the repository: Not defined in repository.

## Decision Summary

Repository artifacts move through explicit, evidence-bearing lifecycle states: Draft, Proposed, Reviewed, Approved, Published, Active, Historical, Deprecated, and Archived. Only explicitly approved artifacts accepted into repository history can become Published, and only artifacts explicitly established as current authority for their scope can become Active. Branch, pull-request, historical, deprecated, and archived artifacts do not become Active merely because they exist. This decision defines governance treatment only and grants no implementation, architecture, roadmap, milestone, release, or version authority.

## History

| Date | Status | Record |
|---|---|---|
| 2026-07-30 | DRAFT | Governance Decision 002 skeleton created in commit `7eec0cc`. |
| 2026-07-30 | DRAFT | Repository lifecycle draft completed; approval not recorded. |
