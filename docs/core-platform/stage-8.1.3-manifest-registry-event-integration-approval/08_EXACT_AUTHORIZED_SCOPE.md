# Exact Authorized Scope

Runtime files authorized:

`NONE`

The sole authorized implementation path is:

`tests/integration/core_platform/test_document_manifest_registry_event_engine_integration.py`

The existing Stage 6 integration test remains unchanged:

`tests/integration/registry/test_registry_event_engine_integration.py`

No package marker is authorized unless repository import convention first proves
it necessary; that condition requires scope-expansion approval before any change.

The implementation diff must be closed-world and contain exactly the one approved
Stage 8 test path. If another path is required, implementation must stop with
`STAGE 8.1.3 SCOPE EXPANSION REQUIRED`.
