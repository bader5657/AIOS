# Cumulative Verification Results

All commands ran at baseline
`ca2a9b9ea146c74c42bb56724643d3c65e95781c` with no test or runtime edits.

| Gate | Scope | Result |
|---|---|---|
| Asset Pipeline focused | `tests/unit/pipeline/test_asset_pipeline.py` | **9 passed, 16 subtests passed** |
| Focused integration | Universal Ingestion, Request Context, capability matrix, lifecycle boundaries | **25 passed, 43 subtests passed** |
| Storage/Metadata/Manifest/schema | Storage path, Telegram boundary, Metadata, Document Manifest | **43 passed, 115 subtests passed** |
| Full Core Platform plus Pipeline | `tests/unit/core_platform tests/unit/pipeline` | **80 passed, 174 subtests passed** |
| Domain Foundation regression | `tests/unit/domain` | **212 passed, 454 subtests passed; 3 existing collection warnings** |
| Compile | `python -m compileall` over Core and relevant tests | **PASS** |
| AST/import dependency audit | Pipeline and all Storage modules | **PASS** |
| Duplicate/no-state audit | Pipeline source/tree | **PASS** |
| Registry/PostgreSQL/network scan | Relevant runtime | **PASS / ABSENT** |
| Schema/meta-validation | Document Manifest focused and full Core suites | **PASS** |
| Repository cleanliness | `git diff --check`; `git status --short` | **PASS / CLEAN** |

The three Domain warnings are unchanged `PytestCollectionWarning` notices for
helper classes with constructors. They are not failures and are unrelated to
Stage 4.
