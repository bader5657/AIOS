# Exact Authorized Scope

Only these runtime paths are authorized:

```text
core/ingestion/universal_ingestion.py
```

Only these test paths are authorized:

```text
tests/integration/core_platform/test_event_engine_aios_core_boundary_integration.py
tests/integration/core_platform/test_document_manifest_registry_event_engine_integration.py
tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py
tests/unit/core_platform/test_universal_ingestion.py
```

The new focused test owns Stage 8.1.4 evidence. The two existing tests may be
modified only to replace now-obsolete static AIOS Core prohibitions with
stage-correct assertions while preserving all Stage 8.1.3 ordering,
transaction, failure, retry, deduplication, and AIOS Core non-execution evidence
for no-event/Event-failure paths.

The Universal Ingestion unit test may change only where the new optional
dependency and mandatory Event-success/Core-call contract require injection or
new result expectations. No unrelated ingestion behavior may be rewritten. No
other runtime or test path may change.

If another runtime path, Event Engine API change, AIOS Core API change,
EventEnvelope change, Registry result change, or additional test path is
required, stop with:

`STAGE 8.1.4 CONTRACT/SCOPE CORRECTION REQUIRED`
