# Constraints and Index Policy

## Approved Constraints

- primary key on database-local `record_id`;
- required/non-null treatment for `record_id`, `identity_ref`,
  `represented_media_type`, `metadata`, `relationships`, and `manifest_ref`;
- JSONB type constraint requiring `metadata` to be an object; and
- JSONB type constraint requiring `relationships` to be an array.

No Stage 3.3.1 metadata field schema is duplicated in PostgreSQL constraints.
No status vocabulary constraint is authorized.

## Uniqueness

Only primary-key uniqueness is approved. `identity_ref`, `manifest_ref`,
`storage_path`, source URL, checksum, metadata, and relationships are not
UNIQUE. No domain deduplication behavior is inferred.

## Indexes

Only the index automatically required by the primary key is approved.
Secondary, JSONB, relationship, status, URL, Manifest, and file-location
indexes are deferred until approved query patterns provide evidence.
