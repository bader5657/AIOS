# Adapter Runtime Contract

The primary entrypoint remains `async handle_update(update, context)` and it
must call the existing `async ingest_telegram_message(...) -> IngestionResult`
exactly once for an eligible message. No second ingestion entrypoint is allowed.

The implementation must remove the adapter import and call of
`RequestContext.from_telegram(...)`. Response formatting may use fields already
returned by `IngestionResult`; it must not recreate RequestContext ownership.

For ordinary non-command text, the exact original Telegram Message object and
its text are passed unchanged. No adapter normalization or link/media
classification is allowed. The current local `(text or "").strip().lower()` may
remain solely for the already-existing exact plain-text `status` match.

The existing `/start` CommandHandler and plain-text `status` response remain
outside general ingestion. Their meaning and routing must not be expanded.
