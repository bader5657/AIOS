# AIOS Governance Decision 007

Status:
DRAFT

Decision ID:
GD-007

## Purpose

Define repository change management, classification, evidence, reversal terminology, and historical preservation. This decision authorizes no change or implementation.

## Scope

Change Requests, review, approval, implementation, verification, release, documentation, historical recording, change classification, rollback, revert, and superseded or historical documents.

## Background

Accepted Git history records documentation, feature, test, milestone, release, and governance commits. [E3] Governance Decision 001 records an approval process and preserves named repository areas from change. [E1] Governance Decision 002 requires explicit lifecycle transitions and retention of Historical and Archived artifacts. [E2] Release Review v0.4 ties review and verification to an exact baseline and accepted Git history. [E4]

A repository-wide Change Request template, issue tracker, change advisory body, required reviewer count, rollback runbook, revert approval shortcut, and retention duration: Not defined in repository.

## Definitions

- **Change Request:** A repository proposal identifying the target, scope, classification, rationale, and requested authority. Required storage and template: Not defined in repository.
- **Review:** Evidence-based assessment of the proposed or completed change within declared scope. Review is not approval. [E2]
- **Approval:** Explicit Project Owner authorization for the declared change and scope. [E1]
- **Implementation:** Modification of repository artifacts within approved scope. This document does not authorize it.
- **Verification:** Accepted evidence that the implemented change satisfies its declared scope. Verification method depends on the change; repository-wide methods: Not defined in repository.
- **Release:** Approval of an exact repository baseline for a declared release scope. [E4]
- **Documentation:** Repository records needed to describe or govern a change. Required document set by classification: Not defined in repository.
- **Historical recording:** Preservation of the proposal, decision, accepted change, reversal or supersession, and relevant evidence in auditable repository history.
- **Rollback:** Restoration of an earlier operational or repository baseline. Runtime rollback procedure and authority: Not defined in repository.
- **Revert:** A new repository change that reverses all or part of an accepted change while preserving the original history.
- **Superseded document:** A retained document whose current authority has been replaced by an explicitly identified later authority. Supersession mechanism beyond Governance Decision 002 Deprecated or Historical treatment: Not defined in repository.
- **Historical document:** A retained artifact evidencing an earlier repository state and not current authority. [E2]

## Change Classification

Each proposed change must identify every applicable class. Classification alone does not grant authority or determine product version.

- **Major:** A proposed change represented as having major scope or compatibility impact. Repository-wide quantitative threshold and mandatory `VERSION` mapping: Not defined in repository.
- **Minor:** A proposed change represented as having limited additive or behavioral scope. Threshold and mandatory `VERSION` mapping: Not defined in repository.
- **Patch:** A proposed correction represented as preserving the surrounding approved scope. Threshold and mandatory `VERSION` mapping: Not defined in repository.
- **Documentation:** Changes only repository documentation.
- **Governance:** Changes governance records, status, or rules; it does not grant implementation authority by classification.
- **Implementation:** Changes source or other implementation artifacts.
- **Testing:** Changes tests or verification artifacts.

A change may be both major, minor, or patch and one or more artifact classes. Classification disputes do not create authority. Resolution method beyond Project Owner decision: Not defined in repository.

## Authority

The Project Owner is the approval authority recorded by Governance Decision 001 and the Domain Foundation Master. [E1] [E5] Authors, implementers, testers, reviewers, and documenters gain no independent approval authority from those roles. Emergency authority: Not defined in repository.

## Rules

The governed change record follows these evidence stages:

```text
Change Request → Review → Approval → Implementation → Verification
→ Release, when applicable → Documentation → Historical recording
```

1. A Change Request must identify scope, targets, classification, rationale, and requested authority before approval.
2. Review must record evidence and outcome. Review does not approve the change. [E2]
3. Approval must be explicit and scope-limited. Approval of a request does not approve out-of-scope implementation.
4. Implementation must remain within approved scope and be accepted into repository history before being represented as repository baseline content.
5. Verification must identify the exact implemented baseline and declared scope. [E4]
6. Release is applicable only when explicit release approval is sought and recorded; implementation or verification alone is not release approval.
7. Documentation must accurately record the accepted change without altering unrelated authority.
8. Historical recording must preserve prior accepted records and link a revert or supersession to the affected record when identifiable.
9. Rollback and revert are changes and require scope, authority, verification, and historical recording. A special emergency bypass: Not defined in repository.
10. A reverted change remains visible in Git history; a revert does not rewrite the original record.
11. A superseded document must be retained in repository history and must not be treated as current authority. Its replacement must be explicit when proven.
12. Historical artifacts must remain traceable and must not become Active automatically. [E2]
13. Major, minor, and patch classification does not itself change `VERSION`; GD-005 requires an explicit accepted `VERSION` edit.
14. Documentation-only and governance changes do not authorize source, test, architecture, roadmap, milestone, release, version, or runtime changes.

Historical document
never disappears.

Repository history
must remain auditable.

“Never disappears” requires preservation in accepted repository history; it does not require every historical file to remain in the current tree. Governance Decision 002 recognizes historical artifacts retained in Git history but absent from the current tree. [E2]

## Conflict Resolution

Governance Decisions 001 and 002 govern this decision. Current explicit authority governs within its declared scope; a superseded or historical record cannot override it. Conflicting or absent change evidence creates no approval. Resolution authority beyond the Project Owner: Not defined in repository.

## Governance Scope

Repository change records, classifications, evidence stages, reversals, supersession, and auditability only.

## Out Of Scope

This decision does not create or approve a Change Request; implement, test, verify, release, rollback, or revert anything; supersede a document; rewrite history; change architecture, Blueprint, Roadmap, milestones, `VERSION`, source, tests, Release Review, or runtime state; or define operational incident response.

## Evidence

- **[E1]** `docs/governance/GOVERNANCE_DECISION_001.md` — approval stages, Project Owner approval, and explicit non-impact scope.
- **[E2]** `docs/governance/GOVERNANCE_DECISION_002.md` — lifecycle transitions, Historical, Deprecated, Archived, and Git-history treatment; status `DRAFT`.
- **[E3]** Accepted Git history through 2026-07-30 — documentation, feature, test, milestone, release, and governance commit records.
- **[E4]** `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` — exact baseline, review evidence, verification, accepted history, and release approval.
- **[E5]** `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — Project Owner authority and scope restrictions.

## Decision Summary

Repository changes require a scoped request, review, explicit approval, controlled implementation, verification, release approval when applicable, accurate documentation, and auditable historical recording. Classification does not grant authority or change version. Reverts and supersession preserve prior records; historical documents remain traceable and non-current.

## Affected Artifacts

Only `docs/governance/GOVERNANCE_DECISION_007.md`.

## Implementation Impact

None. Documentation only.

## Approval

This document remains `DRAFT`; approval of GD-007 is not recorded. Approval beyond identified repository authority: Not defined in repository.

## History

| Date | Status | Record |
|---|---|---|
| 2026-07-30 | DRAFT | Skeleton created in commit `7eec0cc`. |
| 2026-07-30 | DRAFT | Change-management governance draft completed; approval not recorded. |
