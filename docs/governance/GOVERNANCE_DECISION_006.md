# AIOS Governance Decision 006

Status:
DRAFT

Decision ID:
GD-006

## Purpose

Define repository milestone governance and evidence gates. This decision does not create, open, advance, approve, release, archive, reopen, or extend a milestone.

## Scope

Milestone lifecycle states, authority, completion, verification, approval, and the repository evidence used to support status.

## Background

The historical Frozen Roadmap records milestone-like areas, including `Not Started`, and requires implementation to be complete and verified before status updates. It prohibits adding scope during implementation. [E3] Historical Project Status names current and next milestones but directs readers to the Frozen Roadmap and says not to invent roadmap items. [E4] Release Review v0.4 expressly does not reopen or extend accepted milestones. [E5]

A current-tree Active Roadmap, current repository-wide milestone register, milestone identifier format, named milestone opener, approval record format, and archive mechanism: Not defined in repository.

## Definitions

- **Milestone:** An explicitly authorized repository scope tracked toward a defined outcome. A status-report mention alone is not authorization.
- **Not Started:** An authorized milestone with no accepted evidence that implementation has begun.
- **In Progress:** An authorized milestone with accepted implementation activity but without satisfaction of all later gates.
- **Completed:** The declared implementation scope has accepted repository evidence of completion. Completion is not verification, approval, or release.
- **Verified:** Accepted verification evidence supports the completed scope. Historical Roadmap update rules require completion and verification before progress updates. [E3]
- **Released:** An exact milestone baseline has an approved Release Review or other explicit repository release approval. Other release mechanism: Not defined in repository.
- **Archived:** The milestone is retained as historical record outside the active working set. Archive mechanism: Not defined in repository.
- **Implementation evidence:** Accepted commits and artifacts demonstrating the declared scope. Required evidence format: Not defined in repository.
- **Verification evidence:** Accepted test, quality, or review records tied to the declared scope and baseline. Release Review v0.4 records tests and audits. [E5]
- **Review evidence:** An accepted review record stating scope, baseline, findings, and outcome. [E5]

## Authority

The Project Owner is the approval authority recorded by Governance Decision 001 and the Domain Foundation Master. [E1] [E6] Only explicit repository authority may open a milestone. No current artifact identifies another role with independent milestone-opening or approval authority. Not defined in repository.

README

Engineering Journal

Project Status

never open milestone.

Only explicit repository authority may open milestone.

## Rules

The milestone lifecycle is:

```text
Not Started → In Progress → Completed → Verified → Released → Archived
```

1. A milestone must be explicitly opened by current repository authority with scope and an identifiable record. Current opening record format: Not defined in repository.
2. **Completion gate:** accepted implementation evidence must cover the declared milestone scope. Historical Roadmap rules require completed implementation before progress update. [E3]
3. **Verification gate:** accepted verification evidence must cover the completed scope and baseline. Completion alone does not satisfy verification.
4. **Approval gate:** explicit Project Owner approval must be recorded before release. Review alone is not approval. [E1] [E2]
5. **Release gate:** an approved release record must identify the exact baseline and scope. Release Review v0.4 provides repository evidence of such a scoped baseline approval. [E5]
6. **Archive gate:** explicit archival status must be recorded without erasing prior milestone evidence. Archive procedure: Not defined in repository.
7. No lifecycle state may be inferred from README, Engineering Journal, Project Status, commit-message wording, branch names, or elapsed time.
8. A later state requires evidence for every preceding gate; missing evidence leaves the later state unproven.
9. Reopening, extending, skipping, or reversing states requires explicit Project Owner authority. Detailed procedure: Not defined in repository.
10. No document may add scope to a frozen roadmap through milestone status reporting. [E3]
11. This decision does not interpret historical commit wording as proof that all lifecycle gates were satisfied.

## Conflict Resolution

Governance Decisions 001 and 002 govern this decision. Explicit current milestone authority controls within its declared scope; descriptive and historical records cannot override it. Missing or conflicting gate evidence does not advance a milestone. Resolution authority beyond the Project Owner: Not defined in repository.

## Governance Scope

Milestone status treatment and evidence gates only.

## Out Of Scope

This decision does not create or change milestones, roadmap scope, architecture, Blueprint, Roadmap, README, Engineering Journal, Project Status, Release Review, `VERSION`, source, tests, release status, or runtime state.

## Evidence

- **[E1]** `docs/governance/GOVERNANCE_DECISION_001.md` — Project Owner approval and governance stages.
- **[E2]** `docs/governance/GOVERNANCE_DECISION_002.md` — explicit lifecycle evidence and review/approval distinction; status `DRAFT`.
- **[E3]** Commit `da9d692`, `docs/AIOS_Roadmap_Frozen.md` — frozen scope, `Not Started`, progress, and completion-plus-verification update rule.
- **[E4]** Commit `e6ac77a`, `PROJECT_STATUS.md` — historical milestone labels, Frozen Roadmap reference, and prohibition on invented items.
- **[E5]** `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` — exact reviewed baseline, verification evidence, approval, and no milestone reopening or extension.
- **[E6]** `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — Project Owner authority.

## Decision Summary

Milestones require explicit repository authority and progress through Not Started, In Progress, Completed, Verified, Released, and Archived using implementation, verification, review, and approval evidence. README, Engineering Journal, and Project Status can report but never open a milestone.

## Affected Artifacts

Only `docs/governance/GOVERNANCE_DECISION_006.md`.

## Implementation Impact

None. Documentation only.

## Approval

This document remains `DRAFT`; approval of GD-006 is not recorded. Approval beyond identified repository authority: Not defined in repository.

## History

| Date | Status | Record |
|---|---|---|
| 2026-07-30 | DRAFT | Skeleton created in commit `7eec0cc`. |
| 2026-07-30 | DRAFT | Milestone governance draft completed; approval not recorded. |
