# Exact Authorized Scope

Authorized runtime paths: `NONE`.

The only authorized verification path is:

`tests/integration/core_platform/test_official_pipeline_ownership_sequence_integration.py`

No existing test or governance path may be changed during verification. If
another test path is required, stop with:

`STAGE 8.2.1 SCOPE EXPANSION REQUIRED`

If evidence proves a runtime defect, stop with:

`STAGE 8.2.1 RUNTIME CORRECTION APPROVAL REQUIRED`

Runtime must not be patched under this authority.
