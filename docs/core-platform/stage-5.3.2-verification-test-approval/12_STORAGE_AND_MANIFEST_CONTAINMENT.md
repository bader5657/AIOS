# Storage and Manifest Containment

Failure verification must prove the Registry never attempts to delete, modify,
relocate, or take ownership of an original file. Database availability cannot
condition the already-completed Store Original step.

The Registry must not delete, rewrite, or mutate a completed Manifest.
`manifest_ref` and `storage_path` remain reference-only values.

Evidence is limited to test/static boundary inspection and disposable Registry
operations. Stage 3/4 files and actual valued originals/Manifests must not be
modified.
