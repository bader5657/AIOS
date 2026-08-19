# Focused Integration Test Contract

The exact authorized test must use local fakes, mocks, and spies only and prove:

1. authoritative RequestContext exists before Asset Pipeline;
2. the same RequestContext object reaches Pipeline exactly once;
3. zero RequestContext reconstruction;
4. approved receipt-time and Telegram contextual mapping;
5. no username, source, complete context, or context-derived text leakage;
6. exact text remains a separate Universal Ingestion input;
7. file flow orders Store Original → Metadata → Manifest;
8. the same successful metadata object reaches Manifest unchanged;
9. Manifest begins only after Metadata succeeds;
10. successful Manifest yields Register handoff readiness;
11. zero Registry execution;
12. Storage failure prevents Metadata and Manifest;
13. Metadata failure prevents Manifest;
14. Manifest failure prevents readiness and valid-looking completion;
15. no retry or fallback; and
16. no canonical/domain/business meaning is assigned to Telegram identifiers.

The test must not use real Telegram, PostgreSQL, network, Registry, Event
Engine, AIOS Core, production execution, or infrastructure.
