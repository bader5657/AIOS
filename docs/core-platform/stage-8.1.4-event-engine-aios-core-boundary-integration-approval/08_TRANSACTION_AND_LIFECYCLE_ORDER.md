# Transaction and Lifecycle Order

The exact approved sequence is:

```text
Registry COMMIT
  → return to Universal Ingestion
  → EventEnvelope construction
  → await EventEngine.process(envelope)
  → successful EventDeliveryResult
  → await AIOSCore.route(the same envelope)
  → CoreRouteResult
  → AIOS_BRAIN_BOUNDARY readiness
```

No transaction spans Registry, Event Engine, or AIOS Core. Core executes after
the Registry transaction has ended. Core failure or exception cannot roll back
Registry or upstream artifacts. There is no distributed transaction.

Accepted Stage 8.1.3 PostgreSQL commit-order evidence is reused. Stage 8.1.4
requires no PostgreSQL replay; its focused test may bind the accepted upstream
prerequisite.
