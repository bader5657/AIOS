# Identity Strategy

## Database-Local Row Identity

`record_id` is a `BIGINT GENERATED ALWAYS AS IDENTITY` surrogate primary key.
It exists only for PostgreSQL row identity, carries no domain/business meaning,
and is not exposed as a canonical Registry identifier by this authority.

## Approved Upstream Identity

`identity_ref` is required text containing the exact approved upstream
identifier/reference. PostgreSQL Registry does not generate, normalize,
reinterpret, or replace it.

No UUID, hash, sequence-as-business-ID, numeric business key, or exact
identifier-generation policy is authorized.
