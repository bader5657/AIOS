# Historical Implementation Inventory

## Public Surface

| Symbol | Historical behavior |
|---|---|
| `AssetPipelineStatus` | `str, Enum` with `RECEIVED`, `STORED`, `METADATA_EXTRACTED`, `MANIFEST_CREATED`, `COMPLETED`, `FAILED` |
| `AssetPipelineResult` | mutable slots dataclass containing enum status, storage path, metadata dictionary, and manifest path |
| `AssetPipeline` | zero-argument construction; no injected dependencies |
| `AssetPipeline.process()` | synchronous orchestration entrypoint |

## Accepted Input

`process()` accepted a positional `source_path: str` and keyword-only
`media_type`, `original_filename`, `telegram_user_id`, `telegram_chat_id`, and
`telegram_message_id`. It accepted no Request Context, upstream recognized
input value, Text, URL-only value, multi-file aggregate, or explicit Stage 3
boundary disposition.

## Orchestration and Output

The method:

1. converted `source_path` to `Path`;
2. raised `FileNotFoundError` if it did not exist;
3. called historical `save_file(str(source))`;
4. called historical `extract_basic_metadata(storage_path)`;
5. called historical `create_document_manifest(...)`; and
6. returned `AssetPipelineResult` with status always `COMPLETED`.

The historical result carried `storage_path`, a metadata dictionary, and
`manifest_path`. There was no returned failure result and no Register handoff
readiness field.

## Dependencies

The runtime imported only Python standard-library modules, its own state enum,
and three Storage modules:

- `core.storage.file_storage.save_file`;
- `core.storage.metadata_engine.extract_basic_metadata`; and
- `core.storage.document_manifest.create_document_manifest`.

It imported no App classifier, Registry, PostgreSQL, ORM, business domain,
Brain, Intelligence, Specialist Router, network client, or external service.
No Storage → App dependency was introduced by this historical patch.

## Historical Capability Limits

- storage always used historical `IMAGE_ROOT` and image-style naming;
- metadata supported file-backed basics and image dimensions only;
- Manifest accepted Telegram scalar identity rather than Request Context;
- only single-file synchronous input was modeled;
- no Text, URL-only, ten-input, multi-file, or aggregate readiness behavior;
- no retry, recovery, rollback, compensation, transaction, or cleanup policy;
- no duplicate detection or idempotency behavior;
- no Registry or PostgreSQL behavior; and
- no network behavior.
