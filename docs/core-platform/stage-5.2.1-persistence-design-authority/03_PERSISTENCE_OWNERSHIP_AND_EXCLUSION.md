# Persistence Ownership and Exclusion Boundary

PostgreSQL Registry owns persistence of structured registration information in
exactly five categories: identity, approved metadata, approved relationships,
approved registration status/disposition, and file location/reference.

It does not own:

- original business-file binary content or filesystem storage;
- metadata extraction or semantics;
- Document Manifest content, construction, or filesystem ownership;
- Request Context wholesale persistence or semantics;
- business-domain concepts or relationships;
- a canonical Registry Entry;
- runtime Register/read/update behavior; or
- production database operation.

Storage remains owner of originals. Metadata remains governed by Stage 3.3.1.
Document Manifest remains governed by Stage 3.4.1. Stage 5.1.1 remains the
responsibility authority and is unchanged.
