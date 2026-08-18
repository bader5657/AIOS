# Document Manifest Persistence Decision

**Decision: persist `manifest_ref` only.**

`manifest_ref` is required and refers to the successfully completed Document
Manifest. The PostgreSQL Registry must not embed, duplicate, mutate, rebuild,
or reinterpret the complete Manifest.

Document Manifest semantics and serialization remain under Stage 3.4.1.
Filesystem/storage ownership remains unchanged. The exact runtime method by
which a reference is resolved is deferred.
