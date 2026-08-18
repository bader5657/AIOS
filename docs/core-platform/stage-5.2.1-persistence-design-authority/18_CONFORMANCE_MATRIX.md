# Conformance Matrix

| Area | Higher/active authority | Approved design | Result |
|---|---|---|---|
| Five categories | Blueprint; Stage 5.1.1 | Exactly identity, metadata, relationships, status, file location/reference | PASS |
| PostgreSQL | Blueprint | Ordinary native PostgreSQL table | PASS |
| Original binary | Blueprint; Stage 5.1.1 | No binary column or embedded content | PASS |
| Metadata semantics | Stage 3.3.1 | Snapshot only; semantic validation remains upstream | PASS |
| Manifest | Stage 3.4.1 | Required reference only | PASS |
| Storage ownership | Blueprint/Stage 3 | References only; original remains external | PASS |
| Registry Entry | Canonical Model; Stage 5.1.x | Remains unresolved; row explicitly non-canonical | PASS |
| Historical Registry | Stage 5.1.2 | No restoration or historical default | PASS |
| Duplicate behavior | Not authorized | No domain uniqueness constraint | PASS |
| Schema authority | Execution Plan 5.2.1 | Explicit database-local design | PASS |
| Migration authority | Execution Plan 5.2.1 | Versioned SQL approach; no artifact/execution | PASS |
| Transaction authority | Execution Plan 5.2.1 | Single-registration atomic boundary, READ COMMITTED | PASS |
| Runtime | Reserved for Stage 5.3.1 | Absent | PASS |
| Architecture/Roadmap | Higher authority | Unchanged | PASS |
