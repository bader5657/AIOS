# Stage 3.2.2 Minimum Contract Verification

| Control | Value |
|---|---|
| Lifecycle | **PROPOSED EVIDENCE** |
| Verification effect | Governance evidence only; no tests executed or changed |

| Contract requirement | Governance result |
|---|---|
| Complete Image/Voice/Audio/Video/PDF/DOC/DOCX/Spreadsheet mappings | PASS — explicit table in `01` |
| Web/YouTube URL-only non-file disposition | PASS — retained and explicitly excluded from file-ordering inference |
| Manifest path-only later boundary | PASS |
| UUID v4 and validated final extension | PASS — Active Stage 3.2.1 contract retained |
| Original filename separate | PASS |
| Exclusive-create/no overwrite/no rename/no retry | PASS |
| Audio and Video root sharing without reclassification | PASS |
| Non-migration and existing data NO TOUCH | PASS |
| Mixed/multiple originals | PASS — all members, exactly once, all-success barrier |
| Partial/failure disposition | PASS — retained partials, request failure, no downstream progress |
| Metadata responsibility | PASS — Metadata Engine only after aggregate success |
| Manifest and PostgreSQL boundaries | PASS — later owners; no Stage 3.2.2 runtime/schema/reference |
| Compatibility | PASS — Stage 3.1.3, 3.1.4, and 3.2.1 unchanged |
| Exact targets | PASS — two source, three tests; closed world |
| Runtime exclusions and stop conditions | PASS |

**MINIMUM CONTRACT: COMPLETE FOR REVIEW**

## Mandatory Verification Matrix

| ID | Verification | Required evidence/result |
|---|---|---|
| VM-01 | Explicit class/root mapping for every canonical input and Manifest | Exact table match; no inferred root |
| VM-02 | Image, Voice, Audio, Video, PDF, DOC, DOCX, Spreadsheet positive path | Each recognized file original stored exactly once; no Metadata call before aggregate success |
| VM-03 | Original filename and extension boundary | Exact received filename retained separately; stored basename remains UUID v4 plus accepted extension |
| VM-04 | Mixed request with two or more file originals | Every distinct member stored exactly once; no precedence, collapse, or silent discard |
| VM-05 | Aggregate success ordering | Call trace is all Storage completions before first Metadata, then Manifest; no downstream runtime |
| VM-06 | First/middle/final member failure | Request failure; zero Metadata/Manifest/later calls; successful earlier originals retained; zero retry/rollback |
| VM-07 | Collision/write/download failure | Bounded failure; existing target unchanged; no rename, overwrite, or retry |
| VM-08 | Web and YouTube Link | Exact URL identity retained; no file-ordering reclassification, fetch, normalization, serialization, or remote persistence |
| VM-09 | Manifest and PostgreSQL | Manifest remains after Metadata; no Stage 3.2.2 Manifest write/schema or PostgreSQL access/reference/runtime |
| VM-10 | Compatibility | Stage 3.1.3 recognition, Stage 3.1.4 lifecycle, and Stage 3.2.1 storage contract unchanged |
| VM-11 | Runtime/dependency boundary | No Registry, Event Engine, AIOS Core, Brain, Router, Specialist, Intelligence, response, dependency, or schema growth |
| VM-12 | Closed-world diff | Only two allowed source and three allowed test files changed |
| VM-13 | Regression | Targeted, Core Platform, full repository, authority, minimum-contract, and diff checks PASS |

## Mandatory Commands

```text
python -m py_compile core/storage/telegram_storage.py core/ingestion/universal_ingestion.py
python -m pytest -q tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_storage_path_contract.py
python -m pytest -q tests/unit/core_platform
python -m pytest -q
git diff --check
git diff --name-only
```

Authority verification must additionally prove package ancestry, Published and
Active status, unchanged frozen/architecture files, exact target compliance,
and absence of runtime-data contact.
