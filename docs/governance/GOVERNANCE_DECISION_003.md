# AIOS Governance Decision 003

Status:
APPROVED
ACTIVE

Decision ID:
GD-003

## Purpose

Define repository branch and merge governance only. This decision grants no implementation, release, milestone, architecture, or roadmap authority.

## Scope

Branches, pull requests (PRs), merges, and the authority of content before and after acceptance into AIOS repository history.

## Background

The current branch is `main`; Release Review v0.4 reviewed `main`, identified a baseline commit, and checked a clean tracked tree. [E3] Remote `sprint-17-shoegabox-customer` and `sprint-18-conversation-engine` branches exist. [E4] Governance Decision 001 ties official-record effect to commit. [E1] Governance Decision 002 states that branch or PR existence does not create authority and defines artifact lifecycle treatment. [E2]

Repository-wide PR workflow, required reviewer count, branch protection, release-branch naming, hotfix procedure, retention period, and archive mechanism: Not defined in repository.

## Definitions

- **Main branch:** `main`, identified by repository state and Release Review v0.4. [E3] [E4]
- **Feature branch:** A branch containing proposed work before acceptance into `main`. Two remote `sprint-*` examples exist; a mandatory naming convention: Not defined in repository.
- **Release branch:** A branch reserved for release preparation. Naming, creation, and maintenance policy: Not defined in repository.
- **Hotfix branch:** A branch reserved for a proposed urgent correction. Naming, qualification, and maintenance policy: Not defined in repository.
- **Historical branch:** A retained branch recording earlier work or repository state; it is not current implementation merely because it remains addressable.
- **Archived branch:** A branch explicitly outside the active working set and retained for record. Archive location and mechanism: Not defined in repository.
- **PR:** A proposed change and review record before acceptance. Repository-specific tooling and lifecycle: Not defined in repository.
- **Merge:** Acceptance of content into a target branch and its Git history. Merge does not independently establish approval or Active authority. [E2]

## Authority

The Project Owner is the authority identified by Governance Decision 001 and the Domain Foundation Master. [E1] [E5] Branch authors, contributors, reviewers, and PR authors gain no approval authority from those roles.

Before merge, branch and PR content is proposed and has no repository authority. After merge, content is accepted history on the target branch, but its lifecycle and substantive authority remain limited by Governance Decision 002 and its explicit status and scope. [E2]

Open PR
!=
Repository authority.

Remote branch
!=
main.

Historical branch
!=
Current implementation.

## Rules

1. Work not accepted into `main` must not be represented as current `main` content.
2. Feature, release, hotfix, historical, and archived branches gain no authority from local or remote existence.
3. A PR must identify its proposed target and scope. Further PR template requirements: Not defined in repository.
4. Review is not approval, and approval is not merge. [E2]
5. Merge requires an accepted Git change on the target branch. Reviewer count, named reviewers, automated gates, merge strategy, and protection enforcement: Not defined in repository.
6. Merged artifacts become Published or Active only by independently satisfying Governance Decision 002. [E2]
7. A rejected PR remains non-authoritative. Required rejection record, retention, and branch disposal: Not defined in repository.
8. An abandoned branch remains non-authoritative. Abandonment criteria, notice, retention, deletion authority, and recovery: Not defined in repository.
9. Historical and archived branches are not evidence of current implementation without a current accepted baseline establishing that fact.
10. Release and hotfix branch names grant no special authority. Their workflows and approval gates: Not defined in repository.
11. PR lifecycle beyond Governance Decision 002 artifact treatment: Not defined in repository.

## Conflict Resolution

Governance Decisions 001 and 002 govern this decision. Explicit current authority for a specific artifact governs within its scope. Conflicting or absent branch, PR, merge, status, or authority evidence creates no authority. Resolution authority beyond the Project Owner: Not defined in repository.

## Governance Scope

Only the repository meaning of branches, PRs, merges, and retained branch history.

## Out Of Scope

This decision does not create, rename, merge, archive, or delete a branch; act on a PR; define CI or hosting configuration; change architecture, Blueprint, Roadmap, milestone, release, `VERSION`, source, tests, or runtime state.

## Evidence

- **[E1]** `docs/governance/GOVERNANCE_DECISION_001.md` — approval process and official-record effect upon commit.
- **[E2]** `docs/governance/GOVERNANCE_DECISION_002.md` — Active artifact lifecycle and branch/PR authority constraints.
- **[E3]** `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` — reviewed `main` baseline, Git history, and clean-tree review.
- **[E4]** Git branch state on 2026-07-30 — local `main`, `origin/main`, and two remote `sprint-*` branches.
- **[E5]** `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — Project Owner authority.

## Decision Summary

Branch and PR content is proposed and non-authoritative before acceptance. Acceptance into `main` establishes repository history, not automatic approval or Active authority. Remote, historical, and archived branches do not represent current implementation by existence alone. Unspecified branch and PR procedures remain not defined in repository.

## Affected Artifacts

Only `docs/governance/GOVERNANCE_DECISION_003.md`.

## Implementation Impact

None. Documentation only.

## Approval

The Project Owner explicitly approved Governance Decision 003 on 2026-07-30.
Its approved substance is Active for its declared scope.

## History

| Date | Status | Record |
|---|---|---|
| 2026-07-30 | DRAFT | Skeleton created in commit `7eec0cc`. |
| 2026-07-30 | DRAFT | Branch and merge governance draft completed; approval not recorded. |
| 2026-07-30 | APPROVED / ACTIVE | Explicit Project Owner approval recorded; approved substance activated for its declared scope. |
