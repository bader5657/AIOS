# Baseline, Authority, Scope, and Endpoint

The Stage 8.1.3 implementation approval was published at main baseline
`1c861fc1d778b63bede2e79d7f8b56b1cb9eb31c`, with its recorded authority
baseline at `cd44f4b2fd0b18cc2e716ba9619e0ac7d00dfb1e`. It authorized exactly:

`tests/integration/core_platform/test_document_manifest_registry_event_engine_integration.py`

PR `#61` merged that single test file at
`dc83a1c4011fd16192a51dc4bb018de15c3808c0`. First-parent scope audit found no
runtime, migration, dependency, configuration, Blueprint, Roadmap, or
architecture change.

The Project Owner now narrowly expands scope for governance documentation only.
This does not expand runtime, test, behavior, or implementation authority.

The verified lifecycle and endpoint are exactly:

```text
completed Document Manifest
  → Universal Ingestion calls PostgresRegistry.register(...)
  → Registry-local READ COMMITTED transaction commits
  → return to Universal Ingestion
  → zero Event Engine calls when DomainEvent is absent
     or one EventEnvelope and await EventEngine.process(envelope)
```

Evidence ends at committed Registry plus Event Engine result, or committed
Registry plus zero Event Engine calls. AIOS Core is outside Stage 8.1.3.
