# Minimum Data-Responsibility Contract

## PostgreSQL Registry Owns

| Category | Minimum responsibility | Explicit limit |
|---|---|---|
| Identity | Persistence responsibility for approved identifiers and references received through the bounded Register handoff | No identifier generation strategy, format, key type, or new identity semantics |
| Metadata | Persistence responsibility for already-approved upstream metadata | No extraction, reinterpretation, enrichment, or new metadata fields; Stage 3.3.1 remains authority |
| Relationships | Persistence responsibility for bounded relationships among already-approved concepts or references | No business relationship semantics and no new domain objects |
| Status | Persistence responsibility for approved registration-lifecycle status or disposition information | No speculative vocabulary, state machine, or transition rules |
| File location/reference | Persistence responsibility for approved stored-file path/reference, applicable source URL, and Document Manifest reference/path | Storage remains file owner; no original binary storage |

Only structured registration information in these five categories is within
the contract. `Persistence responsibility` states architectural ownership of
the intended information; it does not authorize a persistence mechanism or
database operation.

## PostgreSQL Registry Does Not Own

- original business-file binary content or file storage;
- metadata extraction or metadata semantics;
- Document Manifest construction, schema, or semantics;
- Request Context construction or semantics;
- Asset Pipeline orchestration;
- network retrieval or source enrichment;
- business-domain authority or new domain concepts;
- a Registry Entry domain object;
- schema, tables, columns, indexes, migrations, ORM, driver, credentials,
  connections, queries, or transactions;
- runtime Register/read/update behavior.

No absent detail is authorized by implication.
