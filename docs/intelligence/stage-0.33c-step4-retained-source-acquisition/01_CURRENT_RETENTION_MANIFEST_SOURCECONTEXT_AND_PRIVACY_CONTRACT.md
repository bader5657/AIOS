# Stage 0.33C-P4R Current Retention, Manifest, SourceContext, and Privacy Contract

## Existing ordinary Telegram path

Repository and runtime truth establish the ordinary path:

`Telegram MessageHandler -> ingest_telegram_message -> run_asset_pipeline ->`
`save_telegram_attachment -> save_file -> extract_basic_metadata ->`
`create_document_manifest -> Registry handoff`.

The deployed `aios.service` already runs
`/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main` as
`aiosadmin:aiosadmin`. This is the existing normal production intake, not a new
shortcut or activation. This publication does not send a message, restart or
change the service, read its secret, or invoke ingestion.

For this first genuine source, the currently supported ordinary file-backed
forms are:

- Telegram photo, recognized and retained as `image`;
- a Telegram document with `.pdf`, recognized and retained as `pdf`; or
- a Telegram document with `.doc` or `.docx`, recognized and retained as `doc`.

A genuine spreadsheet is technically retained by the same current path but is
not preferred for the first source. Voice, audio, and video are not suitable
first-source forms for a material-receipt document. A generic Telegram document
whose filename does not map to PDF, DOC/DOCX, or spreadsheet is not eligible:
current metadata/manifest vocabulary does not accept generic `document`, and no
shortcut may be added here.

Normal Universal Ingestion subsequently attempts its existing Registry handoff.
That ordinary behavior is not replaced or bypassed. It is distinct from the
later material-receipt duplicate preflight and candidate write. This governance
performs no Registry or PostgreSQL operation; if the ordinary production intake
or its authority is unavailable at execution time, acquisition stops rather
than using a manual path.

## Preserve-original and manifest contract

Storage downloads the Telegram attachment to a temporary file, then `save_file`
copies the exact bytes once with exclusive creation to the current media root
using a generated lowercase UUIDv4 filename and accepted extension. The
temporary download is removed. The retained original must remain a regular,
non-symlink file; no conversion to text-only evidence or discard of the
original is permitted.

`extract_basic_metadata` records the current supported file facts, including
media type, file size, original filename when supplied, MIME when derivable,
format, and image dimensions/mode for an image. `create_document_manifest`
creates a lowercase UUID manifest under
`/opt/aios/data/documents/manifests/<uuid>.json`, calculates stored-original
size and SHA-256, sets `manifest_status` to `created`, records the received UTC
instant and permitted Telegram provenance, validates the current closed schema,
and installs the manifest atomically.

Retention is successful only if a read-only postcheck proves:

1. exactly one new genuine source was accepted through ordinary intake;
2. the manifest and stored original are regular non-symlink files;
3. the manifest filename is a canonical lowercase UUID and equals
   `manifest_id`;
4. current `validate_manifest` passes with no legacy or extra fields;
5. `manifest_status == "created"` and media/metadata relationships agree;
6. the exact manifest byte SHA-256 is recorded for later binding;
7. the stored-original size and recomputed SHA-256 equal both manifest and
   metadata values;
8. MIME/media type and received timestamp are repository-supported; and
9. no harness, authorization artifact, candidate, or material-receipt write was
   produced.

## Canonical SourceContext and identities

The retained manifest reference must satisfy current `SourceContext`: an exact
absolute path directly under `/opt/aios/data/documents/manifests`, named with a
canonical lowercase UUID plus `.json`. A positive Registry record ID may be
bound only if ordinary registration actually succeeded; it must not be
invented, and absence does not permit a fake value.

Future Step 4 binding may use only repository-supported identities: canonical
manifest reference/UUID, SHA-256 of exact manifest bytes, manifest size,
represented media type, UTC received timestamp, stored-original path identity,
stored-original size and SHA-256, MIME/format metadata, and an actual optional
Registry record ID. Raw content and unrelated Telegram identifiers remain
outside the future approval package.

No OCR, AI, filename guess, historical supplier behavior, or acquisition-time
default establishes supplier, document, item, unit, or quantity facts. Those
remain for later `EVIDENCE_DERIVED` or `PROJECT_OWNER_APPROVED` classification.
