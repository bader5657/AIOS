# Identity and Manifest Reference Decision

The Project Owner approves both values below from the exact completed boundary:

- `identity_ref = pipeline_result.manifest_path`
- `manifest_ref = pipeline_result.manifest_path`

The current boundary exposes the completed Manifest path and does not expose
`manifest_id`. No implementation may expose `manifest_id`, alter the Manifest
return contract, extend `AssetPipelineResult` for identity, parse the Manifest,
or infer identity from the filename.

For `identity_ref`, the path is an already-approved bounded upstream reference.
It has no canonical, domain, business, uniqueness, or deduplication meaning.
Registry persists it without generation, normalization, or reinterpretation.

For `manifest_ref`, the same value explicitly references the completed
Document Manifest artifact. Equal values do not make the two persistence
categories canonically equivalent. This is compatible with Stage 5.1’s
approved upstream-reference input and Stage 5.2’s exact upstream
`identity_ref`, required Manifest-reference, and non-unique-column decisions.

PostgreSQL `record_id` remains separate, database-local, and non-canonical.
