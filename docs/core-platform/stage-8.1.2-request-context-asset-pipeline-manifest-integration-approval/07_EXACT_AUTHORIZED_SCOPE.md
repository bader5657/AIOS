# Exact Authorized Scope

## Test

Exactly one path is authorized:

`tests/integration/core_platform/test_request_context_asset_pipeline_manifest_integration.py`

No package marker is authorized because the current repository convention does
not require one.

## Runtime

**NONE**

RequestContext, Universal Ingestion, Asset Pipeline, Document Manifest,
Metadata, Storage, Registry, Event Engine, AIOS Core, and every other runtime
file remain unchanged.

If any second test/config/schema/document/runtime path proves necessary,
implementation must stop with `STAGE 8.1.2 SCOPE EXPANSION REQUIRED`.
