# Exact Authorized Paths

The future implementation closed world contains exactly:

| Path | Authorization |
|---|---|
| `core/adapters/telegram/main.py` | Required and sole runtime owner |
| `tests/integration/core_platform/test_telegram_ingestion_request_context_integration.py` | Required focused integration test |
| `tests/integration/core_platform/__init__.py` | Optional only if repository import conventions prove it necessary |

No other runtime or test path is authorized. In particular:

- `core/ingestion/universal_ingestion.py`: **NO CHANGE**;
- RequestContext runtime: **NO CHANGE**;
- Storage runtime: **NO CHANGE**;
- production configuration and deployment: **NO CHANGE**.

If the existing Universal Ingestion result cannot support the adapter decision
without modification, implementation must stop with
`STAGE 8.1.1 UNIVERSAL INGESTION SCOPE DECISION REQUIRED`.
