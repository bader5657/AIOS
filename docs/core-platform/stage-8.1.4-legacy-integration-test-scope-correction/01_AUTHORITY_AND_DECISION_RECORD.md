# Authority and Decision Record

## Evidence and obsolete expectation

Git history at baseline `8e84fab75790bd8ca471c8db08a799939be36236`
confirms that
`test_successful_registry_commit_precedes_exact_publication` predates the
Stage 8.1.4 wiring. Its historical success path supplies an Event Engine but no
AIOS Core dependency.

The active Stage 8.1.4 approval requires AIOS Core only after
`EventDeliveryResult.success is True`. No DomainEvent, Registry failure, and
bounded Event Engine failure paths remain Core-free. A successful Event Engine
delivery without injected Core must retain the approved explicit dependency
error.

## Project Owner approval

The Project Owner authorizes expectation reconciliation in exactly:

`tests/integration/registry/test_registry_event_engine_integration.py`

The successful legacy path may inject the actual current `AIOSCore()` or a
test-local equivalent conforming to the Stage 7 boundary. The test must retain
its Registry commit visibility, exact EventEnvelope, record-id exclusion,
failure containment, no-retry, and transaction-boundary evidence. Where Core
is observed, it must receive the same EventEnvelope object exactly once.

This decision does not authorize fallback construction in runtime, weaker
missing-dependency behavior, changes to Event Engine or AIOS Core contracts, or
any new retry, persistence, broker, Brain, or distributed transaction behavior.
