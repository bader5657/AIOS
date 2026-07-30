# AIOS Governance Decision 005

Status:
APPROVED
ACTIVE

Decision ID:
GD-005

## Purpose

Define repository authority for the product version recorded in `VERSION`. This decision does not change that file or approve a release.

## Scope

The `VERSION` file, semantic-version identifiers, prerelease labels, stable identifiers, change authority, and events that do or do not change the recorded version.

## Background

`VERSION` contains `0.1.0-alpha`; README and CHANGELOG repeat that identifier. [E3] [E4] [E5] Commit `8420aea` records “AIOS v0.1.0-alpha.” [E6] Release Review v0.4 used those release documents in its authority chain but did not modify `VERSION`. [E7]

A repository-published semantic-versioning standard, promotion schedule, compatibility contract, prerelease numbering convention, and automatic version-change mechanism: Not defined in repository.

## Definitions

- **VERSION file:** The root `VERSION` file. Its accepted content is the repository's recorded product version. [E3]
- **Semantic version:** An identifier shaped as `MAJOR.MINOR.PATCH`, optionally with a prerelease suffix. The repository uses `0.1.0-alpha`; the repository's normative semantic-version specification: Not defined in repository.
- **Alpha:** The prerelease label present in the current identifier. Repository criteria for entering or leaving alpha: Not defined in repository.
- **Beta:** A prerelease label. Repository criteria for beta: Not defined in repository.
- **Release candidate (`rc`):** A prerelease label for a candidate identifier. Numbering and qualification rules: Not defined in repository.
- **Stable:** A version identifier without an alpha, beta, or rc suffix. Repository stability guarantees and qualification rules: Not defined in repository.

These definitions identify version forms only. They do not claim that beta, rc, or stable versions exist in current repository history.

## Authority

The Project Owner is the approval authority evidenced by Governance Decision 001 and the Domain Foundation Master. [E1] [E8] Only the Project Owner, or a contributor acting under explicit Project Owner authorization, may approve a change to `VERSION`. A complete role-based version-maintainer list: Not defined in repository.

A proposed edit has no version authority before acceptance into repository history. After acceptance, `VERSION` is authoritative only for its recorded release identifier and does not create architecture, roadmap, milestone, implementation, or release-review authority. [E2]

## Rules

1. `VERSION` is the version-authority file; README, CHANGELOG, and release documentation must not contradict its accepted value. [E3] [E4] [E5]
2. `VERSION` changes only through an explicit, approved repository change that edits `VERSION` and is accepted into history.
3. Approval to change `VERSION` must identify the new exact value. A release review that does not edit `VERSION` cannot change it.
4. Timing rules for alpha-to-beta, beta-to-rc, rc-to-stable, and major/minor/patch increments: Not defined in repository.
5. A documentation edit, governance decision, branch, PR, merge without a `VERSION` edit, review number, commit, test result, roadmap statement, or milestone status does not change `VERSION`.
6. Version authority does not arise from README, CHANGELOG, or Engineering Journal text when it conflicts with `VERSION`. The current Engineering Journal states `1.0.0` while `VERSION` states `0.1.0-alpha`; Governance Decision 002 classifies the journal as an ongoing record rather than version authority. [E2] [E3] [E9]
7. This decision does not retroactively classify existing changes as major, minor, or patch.

Commit count
!= version

Release Review number
!= product version

Roadmap progress
!= version

## Conflict Resolution

Governance Decisions 001 and 002 govern this decision. For the product version, accepted `VERSION` content governs over descriptive or historical text. A proposed conflicting identifier has no authority. Resolution authority beyond the Project Owner: Not defined in repository.

## Governance Scope

Repository product-version authority and the conditions for changing the `VERSION` record only.

## Out Of Scope

This decision does not change `VERSION`; approve a version or release; define compatibility promises; create a tag, release, milestone, or roadmap entry; alter architecture, Blueprint, Roadmap, source, tests, release review, or runtime state.

## Evidence

- **[E1]** `docs/governance/GOVERNANCE_DECISION_001.md` — Project Owner approval and official-record effect.
- **[E2]** `docs/governance/GOVERNANCE_DECISION_002.md` — Active artifact and `VERSION` lifecycle treatment.
- **[E3]** `VERSION` — `0.1.0-alpha`.
- **[E4]** `README.md` — `0.1.0-alpha` version statement.
- **[E5]** `CHANGELOG.md` — `0.1.0-alpha` release entry.
- **[E6]** Commit `8420aea` — recorded `AIOS v0.1.0-alpha` baseline.
- **[E7]** `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` — accepted release-document authority chain and unchanged version scope.
- **[E8]** `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — Project Owner authority.
- **[E9]** `docs/engineering-journal.md` — journal version text and `IN PROGRESS` status.

## Decision Summary

The accepted root `VERSION` file is the product-version authority. Its current value is `0.1.0-alpha`. Only an explicit Project Owner-approved edit accepted into history changes it; commit count, review number, roadmap progress, and unrelated repository changes do not.

## Affected Artifacts

Only `docs/governance/GOVERNANCE_DECISION_005.md`.

## Implementation Impact

None. Documentation only.

## Approval

The Project Owner explicitly approved Governance Decision 005 on 2026-07-30.
Its approved substance is Active for its declared scope.

## History

| Date | Status | Record |
|---|---|---|
| 2026-07-30 | DRAFT | Skeleton created in commit `7eec0cc`. |
| 2026-07-30 | DRAFT | Versioning governance draft completed; approval not recorded. |
| 2026-07-30 | APPROVED / ACTIVE | Explicit Project Owner approval recorded; approved substance activated for its declared scope. |
