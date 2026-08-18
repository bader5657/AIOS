# Focused Test Scope

The two authorized unit-test files may verify lifecycle ordering, zero/single
call behavior, exact DTO mapping for file-backed, Text, Web Link, and YouTube
Link inputs, bounded success, bounded Registry failure, and preservation of
already-produced results.

The new integration test must exercise the real caller path through Universal
Ingestion into the current Registry against disposable PostgreSQL, verify the
persisted row and returned `record_id`, and verify controlled Registry failure
after Manifest completion without removing upstream artifacts.

Existing Stage 5.3.x, Stage 3/4, Core Platform, Pipeline, and Domain suites are
regression commands only; their files are not authorized for modification.
`tests/unit/pipeline/test_asset_pipeline.py` is likewise a regression test and
is not authorized for edit because no Pipeline change is permitted.
