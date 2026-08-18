# Stage 3.4.1 Exact Future Implementation Scope

## Authorized Candidate Set for a Future Approval

This record defines the maximum candidate set that a later, explicit
implementation approval may authorize. It does not itself authorize edits.

### Runtime

- `core/storage/document_manifest.py`
- `core/ingestion/universal_ingestion.py`, only where proven necessary to pass
  successful metadata, exact received/source context, and canonical recognized
  type into Create Manifest and to preserve failure ordering

### Normative Schema

- `config/ingestion-manifest.schema.json`

### Focused Tests

- a focused Document Manifest test module under
  `tests/unit/core_platform/`;
- `tests/unit/core_platform/test_universal_ingestion.py`;
- `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`;
- `tests/unit/core_platform/test_ingestion_capability_matrix.py`;
- `tests/unit/core_platform/test_storage_path_contract.py` only if needed to
  verify reuse of the already-approved Manifest storage boundary.

No other file is authorized by implication. If implementation proves any other
file necessary, work must stop and the Project Owner must approve scope
expansion before that file changes.

## Required Implementation Outcomes

The later implementation must reconcile runtime and schema to the entire
minimum contract, reuse current storage roots, validate before treating an
artifact as complete, preserve exact metadata/source meaning, and make failures
stop before Register without leaving a valid-looking partial artifact.

## Explicit Exclusions

The future scope must not implement Registry; alter Stage 3.2.x, Stage 3.3, or
Stage 3.3.1; modify Blueprint, Frozen Roadmap, architecture, or execution-plan
authority; retrieve network content; expand media types or metadata authority;
add dependencies without separate approval; or start Stage 3.5 or Stage 5.
