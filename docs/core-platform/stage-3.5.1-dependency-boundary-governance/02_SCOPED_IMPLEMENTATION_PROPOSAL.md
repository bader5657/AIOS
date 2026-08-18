# Stage 3.5.1 Scoped Implementation Proposal

## Status

**PROPOSAL ONLY — IMPLEMENTATION IS NOT AUTHORIZED**

This proposal is the bounded input for a later, separate implementation
approval. Its baseline is
`36a5fb77f005330b6a5a6fa734672f8601ed3d86`.

## Dependency to Remove

Remove only this production dependency:

```text
core.storage.telegram_storage
  -> core.app.input_classifier.InputType
  -> core.app.input_classifier.recognize_telegram_message
```

## Target Behavior

- Input recognition and classification remain outside Storage.
- Ingestion passes the already-recognized neutral media string for each
  original-file storage call, including the single-file path.
- `save_telegram_attachment()` requires only the minimum neutral media value it
  needs to select the attachment and existing storage class.
- The same original attachment, suffix, original filename, storage class,
  stored path, error behavior, and cleanup behavior are preserved.
- Store Original remains before Extract Metadata and Create Manifest.

## Likely Future Runtime Scope

Only these runtime files are likely necessary:

- `core/storage/telegram_storage.py`;
- `core/ingestion/universal_ingestion.py`.

`core/app/input_classifier.py` is not expected to require behavior changes.
If implementation evidence requires changing it or any other runtime file, the
work must stop for scope review rather than expand silently.

## Likely Future Test Scope

- `tests/unit/core_platform/test_telegram_input_boundary.py`;
- `tests/unit/core_platform/test_universal_ingestion.py`;
- `tests/unit/core_platform/test_ingestion_capability_matrix.py`;
- `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`;
- a focused dependency assertion proving
  `core.storage.telegram_storage` no longer imports
  `core.app.input_classifier` (placed in an existing relevant test file unless
  repository conventions require a narrowly named boundary test).

`tests/unit/core_platform/test_storage_path_contract.py` remains a regression
gate and is not expected to require semantic changes.

## Prohibited Scope

- no changes to Stage 3.2.x, Stage 3.3/3.3.1, or Stage 3.4.x authority or
  behavior;
- no Blueprint, Frozen Roadmap, Canonical Model, Layer Architecture, other
  architecture document, or Domain Foundation changes;
- no Registry, PostgreSQL, migration, Stage 4, Stage 5, Brain, Specialist, or
  adapter business-logic work;
- no new general dependency direction;
- no new shared/domain type or storage-local media enum;
- no second classifier, classifier fallback, or filename classification in
  Storage;
- no Registry, Manifest, metadata, storage-path, or lifecycle behavior change;
- no media-type addition, removal, renaming, or expansion;
- no lifecycle reordering; and
- no deployment or runtime data migration.

## Verification Gates

1. Git baseline and approved target scope are recorded before implementation.
2. Runtime diff is limited to approved files; test diff is limited to approved
   focused coverage.
3. Static import audit proves `core.storage.telegram_storage` has no import
   from `core.app.input_classifier` and introduces no new cross-layer import.
4. Every call to `save_telegram_attachment()` supplies the required neutral
   media value; Storage performs no recognition or classification fallback.
5. Focused attachment-selection tests cover image, voice, generic document,
   PDF, DOC/DOCX, spreadsheet, video, audio, unsupported/no-attachment, and
   multi-file originals without adding a media type.
6. Existing capability-matrix, universal-ingestion, lifecycle-boundary,
   storage-path, metadata, and manifest suites pass.
7. The repository-root test command passes under the accepted environment.
8. Review confirms unchanged storage classes, suffix/filename behavior,
   original-before-processing sequence, metadata/manifest behavior, and
   Register handoff boundary.
9. No status or Roadmap progression is claimed from implementation alone.

## Rollback Condition

Rollback the entire future implementation change if any approved media type no
longer stores the same original, attachment selection becomes ambiguous,
storage class/path behavior changes, lifecycle ordering changes, metadata or
manifest behavior changes, a new cross-layer dependency appears, or removal
requires scope beyond the approved runtime/test files. Rollback restores the
exact pre-implementation Git baseline; it does not authorize retaining a
partial boundary change.
