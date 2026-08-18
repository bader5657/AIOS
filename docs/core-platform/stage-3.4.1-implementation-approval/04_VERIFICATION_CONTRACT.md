# Stage 3.4.1 Implementation Verification Contract

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Effect | Every gate is mandatory for later implementation acceptance |

## Mandatory Gates

| ID | Verification | Required result |
|---|---|---|
| VM-01 | JSON Schema validity | Schema parses and validates as a JSON Schema with `$schema`, root `type: object`, explicit `properties` and `required` |
| VM-02 | Runtime/schema conformance | Every successful runtime output validates against the exact normative schema |
| VM-03 | Ten-class coverage | Text, Image, Voice, Audio, Video, PDF, DOC/DOCX, Spreadsheet, Web Link, YouTube Link covered |
| VM-04 | Text conditional rules | Non-file Text omits stored-original fields; file-backed Text requires all three |
| VM-05 | File-backed rules | Exact stored path, measured bytes, and exact-original SHA-256 required |
| VM-06 | Web Link | Exact `source_url`; no file placeholders or remote activity |
| VM-07 | YouTube Link | Exact `source_url`; no file placeholders or remote activity |
| VM-08 | Metadata preservation | Exact bounded successful Stage 3.3 mapping is preserved without semantic mutation |
| VM-09 | No re-extraction | Manifest code neither calls Metadata Engine nor derives new metadata |
| VM-10 | Media-type boundary | `manifest` and unsupported represented types rejected; no second Manifest domain object |
| VM-11 | Closed schema | `additionalProperties: false`; unknown runtime/schema fields rejected |
| VM-12 | Round trip | UTF-8 JSON read/write preserves meaning and approved primitive types; no binary embedded |
| VM-13 | Checksum | Lowercase 64-hex SHA-256 equals exact stored-original bytes and does not replace original-file semantics |
| VM-14 | Timestamp | `received_at` and present `created_at` are UTC RFC 3339; missing timezone/guesses rejected |
| VM-15 | Success ordering | Store Original → Metadata → Manifest occurs in exact order |
| VM-16 | Metadata failure | Prevents Manifest creation and register readiness |
| VM-17 | Manifest failure | Prevents Register/readiness and propagates failure |
| VM-18 | Registry exclusion | No Registry import, call, persistence, migration, or execution exists |
| VM-19 | Network exclusion | No fetch, dereference, download, redirect resolution, enrichment, snapshot, or remote lookup |
| VM-20 | Partial safety | Simulated validation/write/replace failures leave no valid-looking completed artifact |
| VM-21 | Focused regression | All approved focused tests and unchanged storage-path regression pass |
| VM-22 | Relevant full suites | Core Platform and domain discovery run nonzero tests with no failure/error/unapproved skip |
| VM-23 | Compile/static | Approved Python files compile; schema parses; prohibited-import/source scans pass |
| VM-24 | Closed-world diff | Only the seven exact authorized paths changed; authorities and prohibited paths unchanged |

## Required Command Classes

The implementation evidence must include:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile core/storage/document_manifest.py core/ingestion/universal_ingestion.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/unit/core_platform/test_document_manifest.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_storage_path_contract.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v
git diff --check
git diff --name-only <exact-implementation-baseline>...HEAD
```

Schema-meta-validation and output-validation commands must use existing
repository/environment capability or an approval-compliant bounded test
validator; no dependency installation is implicitly authorized. Any nonzero
exit, zero-test discovery, unexpected skip/error, network contact, dependency
request, forbidden path, authority mismatch, or unresolved drift is a STOP.
