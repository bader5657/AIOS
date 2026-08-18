# Ownership, Handoff, and Original-Binary Exclusion

## Ownership Boundary

```text
Storage preserves original content
  → Metadata Engine produces approved metadata
  → Document Manifest creates the approved manifest
  → Register handoff readiness
  → PostgreSQL Registry responsibility boundary
```

The Ingestion Layer produces the completed Manifest-boundary disposition. The
Core Layer placement of PostgreSQL Registry is the consumer at Register. This
package defines conceptual responsibility at that boundary only: no import,
call, endpoint, command, runtime payload, or database interaction is approved.

## Binding Binary Exclusion

Original business-file binary content remains under the accepted Storage
boundary. PostgreSQL Registry may later persist an approved path, reference,
identifier, metadata, relationship, status, applicable source URL, or Manifest
reference, but it must not store the original binary as its primary storage
representation.

PostgreSQL Registry does not replace Storage, move file ownership, mutate an
original, or make database availability a condition for the already-completed
Store Original step.

## Authority Preservation

- Stage 3.3.1 remains metadata authority.
- Stage 3.4.1 remains Document Manifest semantic/serialization authority.
- Stage 4 remains Asset Pipeline authority.
- Request Context retains its existing authority and ownership.
- Register handoff readiness remains distinct from Registry execution.
