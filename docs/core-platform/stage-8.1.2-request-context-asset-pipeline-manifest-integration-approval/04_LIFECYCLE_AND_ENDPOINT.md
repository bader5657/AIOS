# Lifecycle and Endpoint

The exact sequence to verify is:

```text
RequestContext
  → Asset Pipeline
  → Store Original where applicable
  → Extract Metadata
  → Create Document Manifest
  → register_handoff_ready=True
```

For file-backed input, Store Original must occur before Metadata and Metadata
before Manifest. Later failure does not delete, rewrite, or mutate the stored
original. No original binary enters PostgreSQL.

The exact Stage 8.1.2 endpoint is successful Document Manifest creation plus
`register_handoff_ready=True`. Registry execution, persistence, or success is
not part of this stage. Document Manifest → PostgreSQL Registry → Event Engine
integration belongs to Stage 8.1.3.
