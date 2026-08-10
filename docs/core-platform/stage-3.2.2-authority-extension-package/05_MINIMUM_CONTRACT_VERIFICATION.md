# Stage 3.2.2 Minimum Contract Verification

| Control | Value |
|---|---|
| Lifecycle | **ACTIVE, AS CORRECTED BY THE VM-13 RECONCILIATION** |
| Verification environment | Repository execution environment plus Python standard library only |

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
| VM-05 | Aggregate success ordering | Single-original trace remains Storage then Metadata then Manifest; mixed/multiple trace ends after all Storage completions with zero downstream calls |
| VM-06 | First/middle/final member failure | Request failure; zero Metadata/Manifest/later calls; successful earlier originals retained; zero retry/rollback |
| VM-07 | Collision/write/download failure | Bounded failure; existing target unchanged; no rename, overwrite, or retry |
| VM-08 | Web and YouTube Link | Exact URL identity retained; no file-ordering reclassification, fetch, normalization, serialization, or remote persistence |
| VM-09 | Manifest and PostgreSQL | Manifest remains after Metadata; no Stage 3.2.2 Manifest write/schema or PostgreSQL access/reference/runtime |
| VM-10 | Compatibility | Stage 3.1.3 recognition, Stage 3.1.4 lifecycle, and Stage 3.2.1 storage contract unchanged |
| VM-11 | Runtime/dependency boundary | No Registry, Event Engine, AIOS Core, Brain, Router, Specialist, Intelligence, response, dependency, or schema growth |
| VM-12 | Closed-world diff | Only two allowed source and three allowed test files changed |
| VM-13 | Regression | Targeted, Core Platform, full repository, authority, minimum-contract, and diff checks PASS |
| VM-14 | Output compatibility | No new public result field/schema and no representative stored-path selection; existing single-original result remains unchanged |

## Official Verification Mechanism

The official interpreter is the repository execution environment's available
`python3`. The official Stage 3.2.2 runner is Python standard-library
`unittest`. No local developer installation is authority. Installing pytest or
any other dependency is prohibited; a missing non-standard dependency cannot be
repaired as part of verification.

The repository layout requires separate discovery roots. `tests/unit/domain`
is not an importable package from a higher discovery root, while
`tests/unit/core_platform` is independently discoverable. Therefore the full
regression command deliberately executes both roots and must not be shortened
to a zero-test or partially discovered root command.

## Mandatory Commands

```text
PYTHONDONTWRITEBYTECODE=1 python3 -c "from pathlib import Path; [compile(Path(p).read_text(encoding='utf-8'), p, 'exec') for p in ('core/storage/telegram_storage.py', 'core/ingestion/universal_ingestion.py')]"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_storage_path_contract.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v
git diff --check
git diff --name-only
```

The first command is the required no-bytecode syntax-compilation check. The
second is targeted Stage 3.2.2 verification. The third is Core Platform
regression. The fourth is full repository/domain regression: success requires
both discoveries to execute tests and return zero. Any nonzero exit, import or
discovery error, zero-test result for an expected suite, scope mismatch, or
dependency request is a verification failure and requires STOP.

Evidence must record the exact interpreter version, exact commands, discovered
test counts, pass/fail/error/skip totals, exit status, changed-file list,
`git diff --check`, authority baseline, and lifecycle commits. VM-01 through
VM-12 and VM-14 remain unchanged by this correction.

Authority verification must additionally prove package ancestry, Published and
Active status, unchanged frozen/architecture files, exact target compliance,
and absence of runtime-data contact.
