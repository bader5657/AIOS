# Exact Expanded Paths and Test Contract

After activation, the complete Stage 8.1.1 implementation closed world is:

| Class | Path |
|---|---|
| Runtime | `core/adapters/telegram/main.py` |
| Focused integration test | `tests/integration/core_platform/test_telegram_ingestion_request_context_integration.py` |
| Reconciled boundary test | `tests/unit/core_platform/test_telegram_input_boundary.py` |

No fourth path is authorized. No package marker is required by current
repository discovery conventions.

The reconciled boundary test must strengthen, not weaken, its checks by proving:

1. the adapter imports and delegates to Universal Ingestion;
2. the adapter does not import or construct RequestContext;
3. Universal Ingestion remains the sole RequestContext owner;
4. no classifier, Storage, Registry, Event Engine, or AIOS Core ownership leaks
   into the adapter;
5. no reverse adapter dependency, command expansion, Telegram SDK decoupling,
   retry, media-group state, webhook, network, or later-stage behavior appears.

Only the obsolete RequestContext ownership expectation and directly necessary
assertions in this test file may be reconciled.
