# Exact Focused Test Matrix

The focused one-file implementation must cover at minimum:

1. A → B → C registration order;
2. sequential awaited completion;
3. duplicate callable registration invokes both entries;
4. the same envelope processed twice produces two independent attempts;
5. no deduplication or idempotency state;
6. defensive snapshot before invocation;
7. registration during dispatch excluded currently and available later;
8. invalid envelope exact result, zero calls, no retry, then later valid success;
9. no-handler exact result, no retry, then later independent success with a handler;
10. handler failure stops remaining entries with exact completed count;
11. later invocation remains usable after handler failure;
12. `EventEngineRegistrationError` remains an API validation exception;
13. exactly three delivery failure codes;
14. no retry, parallelism, persistence, broker/network, or historical API;
15. EventEnvelope and DomainEvent remain unchanged.

Existing conforming cases may be retained; tests must not duplicate evidence
without need or encode unauthorized guarantees.
