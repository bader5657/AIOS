# Core Platform Stage 0.4.1 Scoped Change Request

## Record

| Field | Value |
|---|---|
| Status | **ACTIVE** |
| Classification | Core Platform source and test implementation change |
| Requested by | Project Owner |
| Target branch | `main` |
| Baseline commit | `1d261faa87806a506a93d2b333c03f2786725753` |
| Execution Plan position | Stage 3 — Main Step 3.1 — Sub Step 3.1.3 |

## Scope

Implement and verify only the accepted Stage 3.1.3 work, in this order:

1. Task 3.1.3-A — Input Classifier;
2. Task 3.1.3-B — Universal Ingestion; and
3. Task 3.1.3-C — Capability Matrix Verification.

Authorized targets are limited to the existing Input Classifier and Universal
Ingestion source modules and focused unit tests required to verify the complete
explicit Blueprint input list within the Active recognition and capability
contracts.

## Rationale

Stage 3.1.3 requires a focused implementation diff and passing
capability-matrix tests after its input and ownership contracts are
authoritative. Those contracts are Active in the accepted baseline.

## Requested Authority

Scope-limited permission to change the authorized source and test targets only
after every applicable Stage 0 gate is complete. This request does not itself
authorize implementation.

## Exclusions

- Blueprint, Canonical Model, Layer Architecture, Authority Hierarchy, Frozen
  Roadmap, Execution Plan, Official Pipeline, and governance redesign;
- new authority, ADR, capability, media type, dependency, service, parser,
  normalization rule, precedence rule, storage layout, or runtime path;
- AI Pipeline, Brain, Specialist Router, Business Specialists, interfaces,
  external integrations, deployment, release, version, or production changes;
- Stage 3.1.4 or any later Execution Plan task.

## Acceptance Criteria

- Task order A → B → C is preserved, with Project Owner review between tasks.
- Every explicit Blueprint input type is handled within Active contracts.
- Focused unit tests and capability-matrix tests pass.
- No excluded artifact or scope is changed.
- Verification identifies the exact implementation baseline and scope.
- Accepted implementation is recorded on target branch `main` under the
  approved working procedure.

## Lifecycle

| Stage | Evidence |
|---|---|
| Draft | Scoped record prepared against baseline `1d261fa`. |
| Proposed | Submitted by explicit Project Owner instruction for Stage 0.4.1. |
| Reviewed | Scope checked against GD-007 and Execution Plan Stage 0.4.1. |
| Approved | Explicit Project Owner instruction approves creation within the declared scope. |
| Published | Accepted into repository history. |
| Active | Current scoped Change Request for Stage 3.1.3 governance processing. |

This record creates no architecture, implementation behavior, or implementation
authority.
