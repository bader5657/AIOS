# Metadata Persistence Decision

**Decision: approved metadata snapshot/copy as required JSONB.**

The Registry persists the complete already-approved Stage 3.3.1 metadata
result supplied at the bounded handoff. The copy avoids reparsing original
files for later permitted querying.

The Registry must not re-extract, enrich, rename, normalize, reinterpret,
invent, or remove metadata fields. PostgreSQL constraints verify only that the
stored value is a JSON object; they must not duplicate Stage 3.3.1 field
semantics or schema.

This persistence copy does not transfer metadata authority from Stage 3.3.1.
