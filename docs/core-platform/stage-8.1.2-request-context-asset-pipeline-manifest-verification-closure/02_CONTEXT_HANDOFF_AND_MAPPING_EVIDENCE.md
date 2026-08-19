# RequestContext Handoff and Mapping Evidence

Focused execution proves Universal Ingestion constructs the authoritative
RequestContext before the Pipeline call and passes that exact object by
identity to `run_asset_pipeline` exactly once. Factory call count is one and
there is no second construction or serialized/reconstructed handoff.

Manifest-facing values are closed to:

- `received_at` in the existing UTC RFC3339 form;
- `user_id` as optional `telegram_user_id`;
- `chat_id` as optional `telegram_chat_id`; and
- `message_id` as optional `telegram_message_id`.

Exact Manifest arguments prove absence of username, source, text, complete
RequestContext, `manifest_id` supplied by Pipeline, Registry identity, and
business/domain identity. Text remains a distinct exact Pipeline argument; the
focused lifecycle deliberately uses context text different from Pipeline text.
