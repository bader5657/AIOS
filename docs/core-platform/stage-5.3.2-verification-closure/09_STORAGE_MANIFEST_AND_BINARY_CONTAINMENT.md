# Storage, Manifest, and Binary Containment

Runtime-source and failure-path evidence found no Storage or Document Manifest
dependency and no file deletion, mutation, relocation, rename, or ownership
operation.

`storage_path` and `manifest_ref` remain reference-only persisted values.
No original body, PostgreSQL binary type, base64 payload, or original-content
serialization exists.

Registry rollback changed only disposable database state and did not touch an
original or Manifest artifact.
