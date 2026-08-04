# Core Platform Stage 0.2.2 Implementation Approval

## Record

| Field | Value |
|---|---|
| Status | **APPROVED — ACTIVE** |
| Approval authority | Project Owner |
| Target branch | `main` |
| Source baseline commit | `1d261faa87806a506a93d2b333c03f2786725753` |
| Accepted Change Request | `cd41dfe` |
| Accepted change controls | `c7d7775` |
| Execution scope | Stage 3 — Main Step 3.1 — Sub Step 3.1.3 only |

## Implementation Scope

The Project Owner authorizes implementation only for:

1. Task 3.1.3-A — Input Classifier;
2. Task 3.1.3-B — Universal Ingestion; and
3. Task 3.1.3-C — Capability Matrix Verification.

Authorized source targets are limited to:

- `core/app/input_classifier.py`;
- `core/ingestion/universal_ingestion.py`; and
- focused tests under `tests/unit/core_platform/` required for Stage 3.1.3.

The task order and review stops in the Active Working Procedure are mandatory.
This approval becomes executable only after Stage 0.4.3 records PASS for the
complete minimum contract set and the Full Authority Trace finds no conflict.

## Exclusions

- Blueprint, Canonical Model, Layer Architecture, Authority Hierarchy, Frozen
  Roadmap, Execution Plan, Official Pipeline, and architecture changes;
- authority documents, ADRs, new authority, new capability, new media type,
  dependency changes, parser design, normalization, precedence, storage layout,
  storage path, service, schema, or database changes;
- Stage 3.1.4 or later work;
- AI Pipeline, Brain, Specialist Router, Business Specialists, interfaces,
  external integrations, deployment, release, `VERSION`, and production state;
- unrelated source, tests, documentation, or working-tree artifacts.

## Acceptance Criteria

- All Stage 0 prerequisites are Active in accepted repository history.
- Work remains within the accepted Change Request and exact authorized targets.
- Task A, then B, then C is implemented with a Project Owner review stop after
  each task.
- Every explicit Blueprint input type is handled within Active recognition and
  capability contracts; no input is silently deferred.
- Focused unit tests and capability-matrix tests pass.
- Applicable repository-root regression tests pass.
- Verification records exact commands, results, diff, baseline, and boundary
  checks.
- No exclusion is changed and no authority or runtime behavior is inferred
  beyond the Active contracts.
- Each approved implementation task is accepted into `main` history before the
  next task begins.

## Lifecycle

| Stage | Evidence |
|---|---|
| Draft | Scope-limited approval prepared from the accepted Change Request. |
| Proposed | Submitted after Stage 0.4.2 change controls became accepted. |
| Reviewed | Scope, targets, baseline, exclusions, and criteria checked against the frozen plan. |
| Approved | Explicit Project Owner instruction grants the declared conditional implementation approval. |
| Published | Accepted into repository history. |
| Active | Current implementation approval for the declared scope, subject to Stage 0.4.3. |

This approval does not mark implementation complete, verified, released, or
accepted before the required work and evidence exist.
