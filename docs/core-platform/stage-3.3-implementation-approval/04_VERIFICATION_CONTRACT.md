# Stage 3.3 Implementation Verification Contract

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Verification effect | Mandatory gate for the later implementation task |

## Mandatory Gates

| ID | Verification | Required result |
|---|---|---|
| VM-01 | Approved classes | Exact coverage of Text, Image, Voice, Audio, Video, PDF, DOC/DOCX, Spreadsheet, Web Link, YouTube Link |
| VM-02 | Required fields | `media_type` for all; `file_size_bytes` for file-backed; `source_url` for URL-only |
| VM-03 | Optional fields | Exact source-derived values or omission; no guesses/default enrichment |
| VM-04 | Text | Exact identity and optional exact character count; no interpretation |
| VM-05 | File-backed classes | Exact preserved-original size and only locally deterministic optional properties |
| VM-06 | URL-only classes | Exact URL, zero network retrieval/redirect/enrichment |
| VM-07 | Validation | Unsupported class and missing/invalid required facts fail deterministically |
| VM-08 | Failure ordering | Metadata failure stops before Manifest and every later handoff |
| VM-09 | Store Original boundary | Extraction occurs only after successful preservation and describes that original |
| VM-10 | Manifest boundary | No Manifest dependency in extraction; Manifest is never a media type |
| VM-11 | Stage 3.2 compatibility | Stage 3.2.1 unchanged; Stage 3.2.2 aggregate-storage stop unchanged |
| VM-12 | Regression | Existing accepted single-original and capability behavior remains passing |
| VM-13 | Closed-world diff | Only two approved source and four approved test paths changed |
| VM-14 | Static/full suite | Compile checks, focused suite, Core Platform suite, and domain regression pass |
| VM-15 | Runtime safety | No production data/service/network/schema/dependency/deployment effect |

## Mandatory Commands

```text
PYTHONDONTWRITEBYTECODE=1 python3 -c "from pathlib import Path; [compile(Path(p).read_text(encoding='utf-8'), p, 'exec') for p in ('core/storage/metadata_engine.py', 'core/ingestion/universal_ingestion.py')]"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/unit/core_platform/test_metadata_engine.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_storage_path_contract.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v
git diff --check
git diff --name-only
```

Any nonzero exit, unexpected skip/error, zero-test discovery, network contact,
dependency request, forbidden changed path, or authority mismatch is a STOP.
