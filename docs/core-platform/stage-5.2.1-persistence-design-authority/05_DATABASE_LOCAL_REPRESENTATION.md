# Approved Database-Local Representation

The initial PostgreSQL Registry persistence representation is one ordinary
PostgreSQL table named `registry_records`.

The table and each row are database-local persistence constructs only. They
are not a canonical Registry Entry, domain entity, aggregate, business object,
API payload, Python model, or authority for runtime package design.

The design uses native PostgreSQL types and JSONB. It requires no database
extension and remains expressible in plain SQL. No ORM-specific schema
authority is created.

Creating the table remains prohibited until later implementation approval and
an approved migration artifact exist.
