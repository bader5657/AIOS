# Closed Implementation File Scope

## Authorized Runtime Files

Exactly these runtime paths may change:

1. `core/pipeline/__init__.py` — new package marker/export surface only;
2. `core/pipeline/asset_pipeline.py` — new contract-first bounded runtime; and
3. `core/ingestion/universal_ingestion.py` — minimum upstream Request Context,
   neutral-value, and Pipeline caller integration.

`core/ingestion/universal_ingestion.py` is required because the accepted Stage
3 orchestration currently resides there and no production Asset Pipeline caller
exists. The integration must move/delegate only the approved orchestration; it
must preserve Universal Ingestion recognition, acceptance, result compatibility,
and multi-file enumeration responsibilities.

## Authorized Test Files

Exactly these test paths may change:

1. `tests/unit/pipeline/__init__.py`;
2. `tests/unit/pipeline/test_asset_pipeline.py`;
3. `tests/unit/core_platform/test_universal_ingestion.py`;
4. `tests/unit/core_platform/test_ingestion_capability_matrix.py`; and
5. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`.

The three existing Core Platform tests require narrow mock/call-boundary updates
because orchestration moves behind the new Pipeline boundary. They may not be
used for unrelated cleanup.

## Closed-World Rule

No other repository path may change. If implementation requires an Adapter,
Request Context, Storage, Metadata, Document Manifest, classifier, schema,
dependency, or other file, implementation must stop with:

`ASSET PIPELINE SCOPE EXPANSION DECISION REQUIRED`
