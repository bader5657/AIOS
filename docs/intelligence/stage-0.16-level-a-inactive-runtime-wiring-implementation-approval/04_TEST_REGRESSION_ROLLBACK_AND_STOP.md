# Test, Regression, Rollback, and Stop Contract

## Focused Level A tests

The existing Universal Ingestion test module must prove at least:

1. default behavior is unchanged with absent Level A inputs;
2. missing semantic data performs no Brain continuation;
3. explicit semantic data with incomplete dependencies fails closed;
4. non-Brain/failed route calls neither Mapper nor Brain boundary;
5. exact eligible `CoreRouteResult` reaches Mapper once without reconstruction;
6. UUIDv4 factory is called exactly once and exact `corr-<hex>` propagates;
7. explicit Level A EventEnvelope carries the same correlation ID;
8. exact semantic data and provenance reach Mapper;
9. Mapper-produced BrainInput reaches the async boundary exactly once;
10. successful and failed InferenceResult identities are preserved;
11. Mapper and Brain-boundary `TypeError`/`ValueError` propagate;
12. unexpected exception and cancellation propagate;
13. no retry, fallback, task creation, blocking, or nested loop exists;
14. no Telegram/business content is inferred automatically;
15. no concrete provider/runtime import or lifecycle exists;
16. no semantic Registry/DB lookup, persistence, content logging, or business
    action exists; and
17. exact import-policy exceptions remain narrow and default-deny.

Use fakes only. No live provider, Ollama, model, network, schema binding,
production composition, service, database mutation, or inference is authorized.

## Required regression matrix

Run and retain the focused Stage 0.16 tests; Stage 0.15 integration; Mapper,
BrainInput, Receiver, Invoker, adapter mock, and Stage 0.3 suites; Core and
Domain regressions; Stage 8 and Stage 9 gates; full repository suite;
compile/static, dependency/import, prohibited-source, `git diff --check`, and
exact four-path closed-world audits. Zero unresolved failures are required.

## Rollback and stop

Rollback reverts only the exact four implementation paths. Stop immediately if
implementation requires another production/test/policy path, RequestContext or
EventEnvelope schema change, AIOSCore change, a new protocol module, concrete
Receiver/provider import, real user data, schema binding, composition,
activation, persistence, or runtime/service mutation. Seek scope expansion; do
not hide the need inside a broad import exception.
