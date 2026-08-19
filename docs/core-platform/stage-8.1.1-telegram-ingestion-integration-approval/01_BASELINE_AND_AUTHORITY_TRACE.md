# Baseline and Authority Trace

The exact implementation baseline is main/origin main commit
`929c48656d569c9457d1a7787b690a55276557eb`, the merge of the accepted and
closed Stage 7 exit gate. The worktree was clean and local main equalled
origin/main after fetch on 2026-08-19.

Controlling authority, in descending relevance:

1. `docs/AIOS_ARCHITECTURE_v1.md` — official pipeline and adapter exclusion.
2. `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1.md`, active Stage 8.1.1
   row — “Integrate Telegram Adapter boundary → Universal Ingestion → Request
   Context”, requiring a passing integration test.
3. `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md` — Telegram Adapter
   owns transport receipt/delivery; Universal Ingestion owns acceptance and
   ingestion; Storage owns Store Original.
4. accepted Stages 2 through 7 contracts and verification closures.
5. the Project Owner decisions recorded in this package.

Repository inspection at the baseline proves that
`core/ingestion/universal_ingestion.py::ingest_telegram_message()` constructs
the authoritative `RequestContext` with `RequestContext.from_telegram(...)`,
while `core/adapters/telegram/main.py::handle_update()` incorrectly constructs
a second instance. Storage retrieval is performed by
`core/storage/telegram_storage.py::save_telegram_attachment()`, requested by
the Asset Pipeline. No stop condition requiring a Universal Ingestion,
RequestContext, or Storage runtime change was found.
