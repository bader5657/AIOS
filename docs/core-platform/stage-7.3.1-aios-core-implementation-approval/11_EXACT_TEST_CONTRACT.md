# Exact Unit-Test Contract

Only `tests/unit/aios_core/__init__.py` and
`tests/unit/aios_core/test_aios_core.py` are authorized. The focused suite must
prove, at minimum:

1. AIOSCore construction and async-only `route`;
2. valid EventEnvelope success, exact sole target, and absent failure fields;
3. invalid non-EventEnvelope failure, exact `INVALID_INPUT`, exact bounded
   reason, and `route_target is None`;
4. repeated same-envelope equality and identical sole-target routing for two
   different valid envelopes;
5. no event-name whitelist and no payload-dependent route;
6. unchanged EventEnvelope and contained DomainEvent;
7. no internal mutable decision state, retry, or persistence;
8. no Event Engine runtime, Registry, Brain, Memory, Specialist Router,
   business, broker, or network dependency/behavior;
9. exactly one positive target and exactly one failure code;
10. historical conversation/router runtime remains absent;
11. full Domain Foundation regression;
12. Stage 6 regression;
13. relevant Core Platform regression;
14. compile/static and dependency/prohibited-source audits; and
15. exact four-path closed-world diff.

No integration test is expected or authorized because Stage 8.1.4 owns
integration and Stage 7.3.1 invokes no downstream Brain.
