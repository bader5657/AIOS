# Registry Integration Regression

No new integration-test path is authorized or expected. The unchanged
`tests/integration/registry/test_registry_event_engine_integration.py` must be
rerun to prove:

- Registry commit is visible before Event Engine processing;
- Registry failure causes zero Event Engine calls;
- bounded Event Engine failure preserves the committed Registry row, original,
  metadata, and Manifest; and
- no compensation or retry occurs.

The relevant Stage 5 Registry integration, isolation, failure, and migration
regressions must also pass.
