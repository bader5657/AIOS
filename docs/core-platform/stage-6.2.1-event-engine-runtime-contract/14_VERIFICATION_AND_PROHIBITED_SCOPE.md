# Verification and Prohibited Scope

The governance package verifies:

1. routing identity is exact `EventEnvelope.event_name`;
2. async API and handler contract are defined;
3. runtime is in-memory only;
4. handlers are sequential in registration order;
5. snapshot isolation is defined;
6. `NO_HANDLER`, `INVALID_ENVELOPE`, and `HANDLER_FAILURE` are bounded;
7. result invariants and completed-handler count are exact;
8. no retry, broker, persistence, or duplicate/idempotency policy exists;
9. no distributed delivery guarantee is claimed;
10. DomainEvent/EventEnvelope ownership and immutability remain intact;
11. publisher, Registry, and AIOS Core boundaries remain separate;
12. config remains non-authoritative;
13. Stage 6.1.2 REPLACE remains controlling;
14. implementation is deferred to Stage 6.3.1 after Stage 6.2.2;
15. integration is deferred to Stage 6.3.2; and
16. the diff is governance-only.

Prohibited now: runtime/tests/config edits, historical restoration, dispatcher
implementation, concrete consumers, publisher wiring, Stage 5 change,
Domain Foundation change, Brain/Specialist/business behavior, infrastructure,
deployment, or starting Stage 6.2.2/6.3 work.
