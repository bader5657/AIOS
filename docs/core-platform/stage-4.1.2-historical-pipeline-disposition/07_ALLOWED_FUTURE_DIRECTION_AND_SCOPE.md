# Allowed Future Direction and Candidate Scope

## Minimum Future Responsibility

A future replacement may implement only the active bounded orchestration and
handoff contract. It must consume the approved Request Context and upstream
recognized input facts, delegate to current Stage 3 capabilities, preserve
their authority, and return only a bounded success/failure disposition.

The concrete API and result type remain subject to a separate Project Owner
implementation approval. No persistent state model is needed.

## Boundary

```text
Universal Ingestion / approved caller
  → approved Request Context and recognized input facts
  → Asset Pipeline bounded orchestration
  → existing Storage and Metadata boundaries as applicable
  → existing Document Manifest boundary
  → bounded result / existing Register handoff readiness
```

Asset Pipeline may coordinate the calls but cannot classify, persist by itself,
extract new metadata semantics, define Manifest semantics, or execute Register.

## Likely Runtime Candidates — Not Authorized Yet

- `core/pipeline/__init__.py`;
- `core/pipeline/asset_pipeline.py`; and
- `core/ingestion/universal_ingestion.py` only if the later approved integration
  requires the narrow caller handoff.

`core/pipeline/state.py` is not a candidate. Request Context and Stage 3 Storage,
Metadata, and Document Manifest modules are dependencies to consume, not
implicit modification targets. Any need to modify another runtime path is a
scope-expansion decision.

## Likely Test Candidates — Not Authorized Yet

- `tests/unit/pipeline/__init__.py`;
- `tests/unit/pipeline/test_asset_pipeline.py` as a new contract-first test,
  not restoration of the historical test;
- selected existing Core Platform ingestion, capability-matrix, lifecycle,
  storage, metadata, Document Manifest, and dependency tests only if explicitly
  named by implementation approval.

No schema, domain, Registry, PostgreSQL, migration, deployment, production,
Brain, Specialist, or business file is a candidate.
