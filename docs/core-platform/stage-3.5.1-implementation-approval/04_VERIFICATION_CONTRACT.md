# Stage 3.5.1 Implementation Verification Contract

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Effect | Every gate is mandatory for later implementation acceptance |

## Mandatory Gates

| ID | Verification | Required result |
|---|---|---|
| VM-01 | Exact forbidden import | `from core.app.input_classifier import InputType, recognize_telegram_message` absent from Storage |
| VM-02 | Storage dependency | No direct or equivalent `core.storage` → `core.app` dependency introduced |
| VM-03 | Classification ownership | Recognition/classification occurs before Storage and remains in App/Ingestion |
| VM-04 | Explicit neutral value | Every storage call receives the applicable existing `.value` string explicitly |
| VM-05 | Attachment selection | Exact Telegram field and file selection behavior unchanged |
| VM-06 | Storage class/path | Existing class, root selection, returned path, filename, and suffix behavior unchanged |
| VM-07 | Single-file path | Existing production single-file path stores exactly once and continues downstream unchanged |
| VM-08 | Ten-class coverage | Text, Image, Voice, Audio, Video, PDF, DOC/DOCX, Spreadsheet, Web Link, and YouTube Link preserved where applicable |
| VM-09 | Store Original lifecycle | Store Original ordering and failure stop unchanged |
| VM-10 | Metadata | Stage 3.3 behavior and inputs unchanged |
| VM-11 | Document Manifest | Stage 3.4 behavior, inputs, and outputs unchanged |
| VM-12 | Registry exclusion | No Registry import, call, persistence, migration, or execution |
| VM-13 | Network exclusion | No new fetch, request, lookup, download source, or network behavior |
| VM-14 | Focused dependency tests | Static dependency and neutral-value tests pass |
| VM-15 | Universal Ingestion | Exact focused regression suite passes |
| VM-16 | Lifecycle boundaries | Exact focused lifecycle suite passes |
| VM-17 | Capability matrix | Exact focused capability suite passes |
| VM-18 | Storage paths | Unchanged storage-path suite passes |
| VM-19 | Core Platform regression | Full discovery runs nonzero tests with no failure/error/unapproved skip |
| VM-20 | Domain regression | Full discovery runs nonzero tests with no failure/error/unapproved skip |
| VM-21 | Compile/static | Authorized Python compiles; AST/source scans and diff check pass |
| VM-22 | Closed-world diff | Only the exact six authorized paths changed; governance and prohibited paths unchanged |

## Static Dependency Gate

Use simple AST/source inspection in an authorized existing test. It must prove
that `core/storage/telegram_storage.py` has no import from
`core.app.input_classifier`, no imported/referenced `InputType`, and no
imported/referenced `recognize_telegram_message`. Inspect all changed runtime
imports to prove no equivalent reverse dependency was introduced elsewhere.
No dependency-analysis framework or new package is authorized.

## Required Command Classes

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile core/storage/telegram_storage.py core/ingestion/universal_ingestion.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/unit/core_platform/test_telegram_input_boundary.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py tests/unit/core_platform/test_storage_path_contract.py tests/unit/core_platform/test_metadata_engine.py tests/unit/core_platform/test_document_manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v
rg -n 'core\.app\.input_classifier|InputType|recognize_telegram_message' core/storage
git diff --check
git diff --name-only <exact-implementation-baseline>...HEAD
```

For the prohibited-symbol scan, no match in
`core/storage/telegram_storage.py` is required; any match elsewhere under
Storage must be reviewed and may not represent an equivalent reverse
dependency. Any nonzero test/compile result, zero-test discovery, forbidden
path, new dependency, network contact, or unresolved behavior drift is a STOP.
