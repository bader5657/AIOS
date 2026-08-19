# Ownership and Delegation Evidence

- Universal Ingestion remains the sole RequestContext constructor.
- The Telegram Adapter imports no `core.app.request_context` symbol and creates
  zero RequestContext objects.
- Focused evidence observes exactly one downstream
  `RequestContext.from_telegram` call and no duplicate context after delegation.
- The original Telegram Message object is delegated unchanged, by identity,
  exactly once; the Adapter does not reconstruct or classify it.
- Ordinary text reaches Universal Ingestion unchanged. Lowercase/strip is used
  only for the local `status` comparison and does not mutate the Message.
- `/start` and plain-text `status` remain outside general ingestion; no command
  redesign occurred.
- `user_id`, `chat_id`, `message_id`, and `username` mapping remains downstream.
  `update_id`, `file_id`, and `media_group_id` remain transport-only and gain no
  canonical or domain identity meaning.
- Telegram Storage/downstream Storage owns file retrieval and persistence. The
  Adapter performs no download, duplicate download, or fallback download.
