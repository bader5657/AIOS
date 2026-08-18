# Exact Unit-Test Contract

Only `tests/unit/event/__init__.py` and
`tests/unit/event/test_event_engine.py` are authorized.

The focused suite must prove:

1. EventEngine construction and one handler registration;
2. valid Process success and exact success-result fields;
3. non-envelope input returns `INVALID_ENVELOPE`, count 0, invokes no handler,
   retries zero times, and leaks no normal public exception;
4. valid envelope continues normally after invalid-input coverage;
5. `NO_HANDLER` for zero matches and no silent success;
6. `HANDLER_FAILURE`, preserved prior count, and remaining-handler stop;
7. multiple async handlers execute sequentially in registration order;
8. snapshot excludes a handler registered during current delivery;
9. handlers are awaited before the next starts;
10. envelope and DomainEvent remain unchanged;
11. exactly three failure-code members and result invariants;
12. no gather/task spawning, retry, persistence, broker/network, config read,
    historical Event, dispatcher API, or reverse domain dependency;
13. Domain Foundation regression passes unchanged;
14. relevant Core Platform regression passes;
15. compile/static and prohibited-source audits pass; and
16. closed-world diff contains exactly four authorized paths.

No integration test is authorized; publisher integration belongs to 6.3.2.
