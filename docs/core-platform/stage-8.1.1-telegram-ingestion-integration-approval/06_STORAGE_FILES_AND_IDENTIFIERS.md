# Storage, Files, and Telegram Identifiers

Storage retains exclusive Telegram file retrieval and original persistence
ownership through the current `save_telegram_attachment()` path requested by
the Asset Pipeline. The adapter must neither call Telegram file download APIs
nor persist/transform files. Original business files are persisted before
metadata extraction; no original binary is stored in PostgreSQL; there is no
duplicate download.

The only approved RequestContext mapping remains:

- `user_id` from the Telegram user id;
- `chat_id` from the Telegram chat id;
- `message_id` from the Telegram message id;
- `username` as a required string using the current empty-string fallback.

`update_id`, `file_id`, and `media_group_id` are transport-only. `file_id` may
be consumed by Telegram Storage for retrieval but is not RequestContext,
Registry, DomainEvent, business, or domain identity. No new identity semantics
are authorized.

For one Message with multiple approved file-backed attributes, preserve only
the deterministic ordering already implemented in Universal Ingestion. Do not
widen it. If a valid result would require broader semantics, stop and report a
scope conflict.
