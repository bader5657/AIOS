# Verification Gates

Implementation is acceptable only when every gate passes:

1. exact Stage 7.2.1 EventEnvelope/API/result/target/failure contract;
2. async-only, stateless, deterministic Route;
3. no payload semantic routing; exactly one target and one failure code;
4. EventEnvelope and DomainEvent immutability;
5. no Brain invocation or Event Engine implementation dependency;
6. no Registry, Memory, Specialist Router, persistence, retry, broker/network,
   business, infrastructure, or new dependency;
7. no historical runtime restoration;
8. all focused unit tests pass;
9. full Domain Foundation regressions pass unchanged;
10. Stage 6 regressions pass unchanged;
11. relevant Core Platform regression passes;
12. compile/static and dependency/prohibited-source audits pass;
13. `git diff --check` passes; and
14. closed-world diff contains exactly the four authorized implementation
    paths and no other change.

No mandatory gate may be skipped.
