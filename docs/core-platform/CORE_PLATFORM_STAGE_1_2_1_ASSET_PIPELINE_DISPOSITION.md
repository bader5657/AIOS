# Core Platform Stage 1.2.1 Asset Pipeline Disposition

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 1 — Main Step 1.2 — Sub Step 1.2.1 |
| Current review baseline | `5cb3073e6a415a01ab49dd08083bb6baa5347983` (`main`) |
| Historical component commit | `9d1288cca4b47d6fca963a8bff16041599b5e5c4` |
| Historical commit subject | `feat(core-platform): add asset pipeline` |
| Historical branch evidence | `origin/sprint-18-conversation-engine` |
| Review method | Read-only source, test, dependency, and authority comparison |
| Component disposition | **ADAPT** |
| Review date | `2026-08-02` |

The historical commit is not an ancestor of current `main` and is not current
implementation. This disposition records how its evidence may be treated in
later authorized work; it does not copy, merge, approve, or activate the code.

## Scope

This review covers only the Asset Pipeline files introduced by commit
`9d1288c`:

| Historical path | Role |
|---|---|
| `core/pipeline/__init__.py` | Package marker |
| `core/pipeline/state.py` | Six named pipeline status values |
| `core/pipeline/asset_pipeline.py` | Synchronous storage/metadata/manifest orchestrator |
| `tests/unit/pipeline/__init__.py` | Test package marker |
| `tests/unit/pipeline/test_asset_pipeline.py` | One image happy-path test |

Registry, Event Engine, AIOS Core, and all later component reviews are excluded.

## Current Authority Used for Comparison

The active Blueprint provides the following Asset Pipeline constraints:

- it is positioned after Request Context and before Document Manifest in the
  official pipeline;
- every original file must be stored before processing;
- the ingestion lifecycle orders Store Original, Extract Metadata, Create
  Manifest, and Register before later processing/routing;
- runtime storage distinguishes image, voice, PDF, document, link, and manifest
  locations;
- Ingestion may depend on App and Storage, and Storage must not depend on Brain
  or Specialists;
- business logic must not be placed in the Telegram Adapter.

The frozen Execution Plan further requires later Asset Pipeline contract,
implementation, integration, and verification work in Stage 4. No approved
minimal Stage 4 Asset Pipeline contract is present at the current review
baseline. Therefore this review does not invent state semantics, failure
policy, duplicate behavior, or integration behavior beyond the explicit
authority above.

## Evidence Comparison

| Historical behavior | Authority/current-baseline comparison | Finding |
|---|---|---|
| `AssetPipeline.process()` checks that a source path exists | Safe local precondition, but not an approved complete validation contract | Candidate for adaptation |
| Calls `save_file()`, then `extract_basic_metadata()`, then `create_document_manifest()` | Preserves the explicit Store Original → Extract Metadata → Create Manifest order | Reusable sequencing evidence |
| Imports the three existing `core.storage` modules | Those dependency files have identical content between `9d1288c` and the current review baseline | Mechanically compatible evidence only |
| Accepts `source_path` and Telegram identity arguments directly | Does not consume the Request Context that precedes Asset Pipeline in the official pipeline | Must adapt |
| Uses current `save_file()`, which writes every attachment through the image root and image-style naming | Does not satisfy the Blueprint's distinct storage classes for all accepted file types | Must adapt after storage contract work |
| Declares `RECEIVED`, `STORED`, `METADATA_EXTRACTED`, `MANIFEST_CREATED`, `COMPLETED`, and `FAILED` | Runtime returns only `COMPLETED`; no transition semantics or failure transition is implemented | States cannot be accepted as a contract |
| Returns storage path, metadata, and manifest path | Potential output evidence, but the approved Asset Pipeline output contract is not yet established | Candidate for adaptation |
| Raises `FileNotFoundError` only for a missing source | No approved error model, cleanup/rollback, retry, duplicate, or partial-failure behavior is implemented | Must adapt; missing semantics remain unresolved |
| One test exercises a JPEG happy path | No invalid, duplicate, transition, or failure coverage; test uses `tmp_path` and `monkeypatch` from `pytest` | Insufficient for reuse |
| Test imports Pillow | Pillow remains pinned in current `requirements.txt` | Dependency remains available |
| Test requires pytest fixtures | No pytest dependency is pinned and no separate test dependency manifest exists in current baseline | Test cannot be adopted blindly |

Static comparison found no changes between the historical commit and current
baseline for `core/storage/document_manifest.py`, `core/storage/file_storage.py`,
`core/storage/metadata_engine.py`, or `requirements.txt`. This confirms source
compatibility with those exact dependencies, but it does not resolve the
authority and contract gaps above.

## Disposition

**ADAPT** the historical implementation only as evidence for later Stage 4
design and implementation review.

Eligible evidence to carry forward:

- the orchestration ordering of storage before metadata and manifest creation;
- separation into a pipeline module and state module as a historical packaging
  candidate, not an approved boundary;
- the result concept and image happy-path scenario as inputs to later contract
  and test design.

Not accepted for direct reuse:

- the `process()` signature and Telegram-specific identity parameters;
- the six status values or their semantics;
- image-root storage behavior for every media type;
- error, failure, duplicate, cleanup, retry, or transition behavior;
- the historical test as sufficient verification; and
- the historical package as current or approved runtime.

Any later adaptation remains dependent on the approved Stage 2 Request Context,
Stage 3 storage/metadata/manifest results, and the Stage 4.1 Asset Pipeline
contract and review. Resolving those dependencies now would exceed Sub Step
1.2.1, so none is implemented here.

## Validation and Result

Review evidence was obtained with read-only Git inspection of commit metadata,
the complete historical patch, the five historical files, current authority,
current-tree absence, branch containment, imports, dependency files, and the
current baseline inventory.

No historical file was copied or merged. No source, test, dependency, schema,
runtime, authority, milestone, freeze, or product-status artifact was changed.

**Sub Step 1.2.1 result: PASS**

Main Step 1.2 remains in progress. The next frozen-plan position is Stage 1,
Main Step 1.2, Sub Step 1.2.2. That Sub Step is not started by this disposition.
