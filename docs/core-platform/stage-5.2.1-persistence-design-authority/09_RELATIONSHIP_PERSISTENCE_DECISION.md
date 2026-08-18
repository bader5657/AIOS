# Relationship Persistence Decision

**Decision: required JSONB array of already-approved bounded relationships.**

An empty array represents no relationships. PostgreSQL may verify only that
the value is an array. This stage defines no relationship vocabulary,
cardinality, direction, target type, business semantics, or foreign-key target.

No foreign key to an unapproved business-domain table is authorized. Future
normalization or relationship indexing requires separate evidence and
authority.
