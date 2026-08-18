# Stage 3.5.1 Scoped Implementation Approval

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Implementation authority | **ACTIVE for the exact approved scope only** |
| Exact baseline | `ef55b65141773739360b3d5e942ef84c5603ce86` |
| Coupling to remove | `core.storage.telegram_storage` → `core.app.input_classifier` |

## Classification and Neutral-Value Contract

Classification remains outside Storage. The authorized flow is:

```text
Adapter → Universal Ingestion → recognize input → pass neutral media string → Storage
```

The neutral value is the existing `InputType.value` string. Ingestion passes
`recognized_input_type.value` for the single-file production path and the
corresponding `file_original_type.value` for each multi-file original. Storage
may use that value only to select the matching Telegram attachment and pass the
same existing storage class to `save_file`.

Storage must not import or reference `InputType`, call or reference
`recognize_telegram_message()`, perform fallback media classification,
reinterpret media semantics, infer a media value from a filename, or accept an
optional/absent media value. Moving App types to another package merely to hide
the dependency is prohibited. No new enum, module, canonical object, or second
source of truth is authorized.

## Existing Behavior to Preserve

- Telegram attachment selection for image, voice, audio, video, generic
  document, PDF, DOC/DOCX, and spreadsheet;
- existing suffix, original filename, storage destination/class/path, temporary
  file cleanup, and `OSError` result behavior;
- Text, Web Link, and YouTube Link bypass of original-file Storage;
- all ten approved input/media identities and current recognition results;
- single-file and multi-file Universal Ingestion behavior;
- Store Original before Extract Metadata before Create Manifest;
- current Metadata mapping and Document Manifest inputs/output behavior;
- capability matrix and register-handoff readiness; and
- absence of Registry execution and network behavior changes.

No lifecycle reordering, media expansion, path change, metadata/Manifest
semantic change, Adapter update, or broader dependency authority is approved.
