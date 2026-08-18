# Update Contract

Approved async operation:

`update(record_id, patch) -> RegistryPersistenceRow | None`

Mutable fields are exactly `metadata`, `relationships`,
`registration_status`, `storage_path`, and `source_url`.

Immutable fields are `record_id`, `identity_ref`, `represented_media_type`,
and `manifest_ref`. The DTO surface must make immutable updates impossible.

An empty patch raises `ValueError` before opening a connection or issuing SQL.
Not-found returns `None`. Success returns the full persisted row. SQL must be
parameterized. No delete, upsert, merge, dedupe, implicit status transition, or
semantic reinterpretation is authorized.
