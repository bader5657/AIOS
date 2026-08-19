# Lifecycle and Handoff Evidence

The test records the actual accepted Asset Pipeline orchestration order:

```text
RequestContext handoff
  → Store Original
  → Extract Metadata
  → Create Document Manifest
  → register_handoff_ready=True
```

Storage, Metadata, and Manifest capabilities are replaced only at their local
external boundaries with spies; the real Universal Ingestion handoff and real
Asset Pipeline orchestration execute.

Metadata extraction occurs once and the exact same metadata object reaches
Manifest construction unchanged. Successful Manifest return supplies the
exact Manifest path, bounded success, and Register readiness. The stored
original is not deleted or mutated and no original binary enters PostgreSQL.
