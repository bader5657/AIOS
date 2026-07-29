# AIOS Governance Decision 004

Status:
DRAFT

Decision ID:
GD-004

## Purpose

Define governance for reviewing and approving a repository release baseline. This decision does not approve a release.

## Scope

Release candidates, review, approval, release notes, release review, baselines, and acceptance recorded in the repository.

## Background

Release Review v0.4 identifies a `main` baseline commit, an authority chain, review gates, evidence, and an `APPROVED` result. It states that no release tag is required by the accepted release process. [E3] `VERSION`, README, and CHANGELOG record `0.1.0-alpha`. [E4] [E5] [E6] Governance Decision 001 records Project Owner approval after named governance stages and limits repository impact. [E1]

A repository-wide release-candidate naming scheme, required release-note format, recurring release calendar, distribution mechanism, and acceptance procedure beyond recorded review: Not defined in repository.

## Definitions

- **Release candidate:** A fixed proposed repository baseline presented for Release Review. Candidate naming and branch requirements: Not defined in repository.
- **Review:** Evidence-based examination of the candidate within a declared scope. Review is not approval. [E2]
- **Approval:** Explicit Project Owner acceptance recorded for the declared scope. [E1] [E2]
- **Release notes:** A repository record describing a release. `CHANGELOG.md` contains the current release entry; a separate required format: Not defined in repository. [E6]
- **Release Review:** A scoped repository record that identifies its baseline, authority, evidence, findings, and approval outcome. [E3]
- **Baseline:** The exact commit and branch reviewed. Release Review v0.4 uses commit `d74350ad24d5cab3bdfb8d2b1ae1319eb8d2c1c4` on `main`. [E3]
- **Acceptance:** Explicit repository evidence that the reviewed baseline was approved for the review's declared scope. Acceptance outside that scope is not established.

## Authority

The Project Owner holds approval authority as recorded by Governance Decision 001 and the Domain Foundation Master. [E1] [E7] A reviewer may record findings but gains no approval authority from review alone. Approval authority for any other role: Not defined in repository.

## Rules

1. A release candidate must identify an exact repository baseline before review.
2. Release Review must state scope, baseline, authority chain, evidence, findings, and outcome. Release Review v0.4 demonstrates these elements. [E3]
3. Review findings apply only to the stated baseline and scope; they do not establish unreviewed runtime state.
4. Approval must be explicit. Draft, Proposed, or Reviewed status is not approval. [E2]
5. Acceptance makes the approved review record part of accepted history when committed, subject to Governance Decision 002 lifecycle rules. [E1] [E2]
6. Release notes must remain consistent with the accepted release identifier and baseline. Detailed format and publisher: Not defined in repository.
7. A Release Review does not require or create a release tag unless current repository authority explicitly requires one. Release Review v0.4 states no tag was required. [E3]
8. Approval of one baseline does not approve later commits.

Release Review
approves
repository baseline.

Release Review
does not

- modify architecture;
- modify roadmap;
- modify `VERSION`; or
- verify runtime outside review scope.

## Conflict Resolution

Governance Decisions 001 and 002 govern this decision. A Release Review is limited by the current authority chain it cites and its declared baseline and scope. Conflicting or missing evidence does not produce approval. Resolution authority beyond the Project Owner: Not defined in repository.

## Governance Scope

Repository release review and baseline acceptance only.

## Out Of Scope

This decision does not approve a release candidate or baseline; create a candidate, tag, branch, milestone, or release; change architecture, Blueprint, Roadmap, `VERSION`, README, CHANGELOG, Domain Foundation, source, tests, or runtime state; or define deployment and distribution.

## Evidence

- **[E1]** `docs/governance/GOVERNANCE_DECISION_001.md` — approval record, Project Owner approval, and publication effect.
- **[E2]** `docs/governance/GOVERNANCE_DECISION_002.md` — lifecycle and review/approval distinction; status `DRAFT`.
- **[E3]** `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` — approved review, exact baseline, gates, evidence, scope limits, and tag statement.
- **[E4]** `VERSION` — `0.1.0-alpha`.
- **[E5]** `README.md` — repository version statement.
- **[E6]** `CHANGELOG.md` — `0.1.0-alpha` release entry.
- **[E7]** `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — Project Owner authority.

## Decision Summary

A Release Review evaluates an exact repository baseline within a declared scope and records evidence and outcome. Explicit approval accepts that baseline only; it does not change architecture, roadmap, version, or unreviewed runtime state.

## Affected Artifacts

Only `docs/governance/GOVERNANCE_DECISION_004.md`.

## Implementation Impact

None. Documentation only.

## Approval

This document remains `DRAFT`; approval of GD-004 is not recorded. Approval beyond identified repository authority: Not defined in repository.

## History

| Date | Status | Record |
|---|---|---|
| 2026-07-30 | DRAFT | Skeleton created in commit `7eec0cc`. |
| 2026-07-30 | DRAFT | Release governance draft completed; approval not recorded. |
