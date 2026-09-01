# Stage 0.33C-P4 Real Retained Evidence Eligibility and Privacy

## Authority, purpose, and non-selection

Steps 1, 2, and 3 are `CLOSED / VERIFIED` at repository baseline
`ffd2585539a51fe5fe7265adff2662a4f97b2971`. Step 4 is current for governance
publication only. This package defines how one later real production source may
be selected; it selects no source, supplier, document, item, quantity, or other
business value. Synthetic production data, invented facts, and LLM-generated
facts are prohibited.

The only permitted future purpose is one `NEEDS_REVIEW` material-receipt
candidate. Expected later effects are one `material_receipts` row and N
`material_receipt_items` rows. Confirmation, posting, inventory movement, and
stock effects must all remain zero. Step 5 first-write authority is not created
here.

## Repository-grounded retained evidence model

The current retained-evidence identity is `SourceContext`: a canonical absolute
manifest reference under `/opt/aios/data/documents/manifests`, whose filename is
a canonical lowercase UUID JSON name. The exact form is
`/opt/aios/data/documents/manifests/<canonical-lowercase-UUID>.json`. The UUID
filename must equal the manifest's `manifest_id`. `registry_record_id` is an
optional positive integer only when actual retained ingestion/registration
evidence supports it; it is not required for source identity and must not be
invented.

A valid `DocumentManifest` supplies these repository-supported facts:

- `manifest_id`, `represented_media_type`, UTC RFC3339 `received_at`, exact
  `manifest_status == "created"`, and type-specific bounded `metadata`;
- for a file-backed source, `storage_path`, `file_size_bytes`, and lowercase
  `checksum_sha256`, with the size duplicated consistently in metadata;
- for a URL-only source, exact `source_url` and matching metadata; and
- optional Telegram identifiers, which are evidence fields but are excluded
  from the Step 4 package unless DTO-purpose necessity is separately proven.

The future evidence binding must record the canonical manifest reference,
manifest UUID, SHA-256 of the exact manifest bytes, represented media type,
manifest received timestamp, and manifest byte size. Manifest bytes must not
exceed the current authorization boundary's 4,194,304-byte maximum. For a
file-backed source it
must additionally record the stored-original byte size and checksum from the
manifest, and the MIME/content type if present. The later selector must
recalculate the exact manifest SHA-256 and, for file-backed evidence, recalculate
the stored-original SHA-256 and size. URL-only evidence has no invented stored
file checksum. The manifest-byte SHA is required for every selected source.

Every retained string projected into `approved-input-approval.json`, including
MIME metadata, must satisfy the approval record's `APPROVAL_SAFE_STRING`
grammar: valid Unicode scalar values excluding U+0000 through U+001F, U+007F,
and U+D800 through U+DFFF. MIME is null or the exact retained value of 1–255
permitted scalars. A prohibited scalar makes the evidence ineligible; stripping,
replacement, trimming, normalization, or any semantic transformation is
prohibited. Fixed identifiers, hashes, timestamps, enums, and references use
their stricter closed grammars rather than generic strings.

No image, PDF, DOC/DOCX, voice/audio/video, spreadsheet, text payload, base64,
raw binary, or raw retained content may be copied into the approval record or
Git. Reference, size, type metadata, and hashes only are permitted outside the
separately controlled retained store.

## Eligibility and existence gate

A later selection must fail closed unless all of the following are proven by a
bounded, source-specific read:

1. the canonical manifest is an existing non-symlink regular file in the exact
   retained manifest root and is retrievable through the governed verifier;
2. it is valid under the current closed `DocumentManifest` schema, its filename
   UUID equals `manifest_id`, and its exact byte SHA-256 matches the selection
   record;
3. any referenced stored original is an existing non-symlink regular file and
   its recomputed size and SHA-256 match the manifest;
4. the evidence predates and was not fabricated for the Step 4 selection; this
   must be supported by retained-ingestion/registry evidence or explicit
   Project Owner attestation bound to the source hashes;
5. there is no integrity, identity, media-type, timestamp, or version mismatch;
   and
6. it satisfies the later candidate-bound duplicate preflight.

This publication performs none of those production reads and selects nothing.
The later harness-native input is bounded at exactly 86,835 canonical semantic
bytes and 86,836 transport bytes including one LF. That larger corrected ceiling
does not permit raw content, extra metadata, or any privacy expansion.

If the real evidence cannot be represented by the existing manifest,
`IngestionResult`, `TrustedReceiptFacts`, and harness contracts, selection stops
for separate architecture/interface governance.

## Privacy and Git boundary

Data minimization is mandatory. Credentials, passwords, financial
authentication data, unnecessary personal identity, unrelated notes, Telegram
metadata not required by the DTO, environment data, authorization state, and
other unrelated content are prohibited. The harness must never accept or
inspect a database password, DSN, runtime environment, token, private key, or
authorization secret through Step 4.

Real supplier, document, receipt, item, quantity, manifest-path, registry ID,
and approval identity values must not enter Git or broadly visible repository
history. Git may contain only this policy, non-sensitive schema/field names,
fixed software identities, and later hashes or opaque approval references if an
independent privacy review declares them safe. The actual canonical input and
approval record belong only in separately governed restricted runtime storage.

Production PostgreSQL contacted: `NO`.

Real retained evidence selected or inspected: `NO`.

Real business values committed: `NO`.

Harness invoked: `NO`.
