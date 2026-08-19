# RequestContext Handoff and Mapping

The focused integration test must prove that the authoritative RequestContext
exists before the Pipeline call and that the exact same object is handed to
`run_asset_pipeline` exactly once. It must prove zero reconstruction and zero
second construction.

The approved mapping is closed:

| RequestContext field | Downstream disposition |
|---|---|
| `received_at` | Required Manifest input after existing UTC RFC3339 serialization |
| `user_id` | Optional `telegram_user_id`; contextual/source relationship only |
| `chat_id` | Optional `telegram_chat_id`; contextual/source relationship only |
| `message_id` | Optional `telegram_message_id`; contextual/source relationship only |
| `username` | Must not enter Metadata or Manifest |
| `source` | Must not enter Metadata or Manifest |
| `text` | Must not be derived from RequestContext; remains a separate exact Universal Ingestion argument |

No complete or serialized seven-field RequestContext enters the Manifest. No
field becomes canonical business/domain identity. The Telegram identifiers
remain optional contextual relationships under the active Manifest contract.
