# Failure Contract

The implementation must preserve these exact boundaries:

- storage failure produces no metadata, Manifest, or downstream success;
- metadata failure produces no Manifest or downstream success;
- Document Manifest failure produces no downstream success/readiness;
- no failure can be represented as success;
- existing Metadata/Manifest exceptions may propagate as the deterministic
  failure path rather than being hidden or translated;
- failed Manifest construction/validation/serialization/persistence leaves no
  valid-looking partial Manifest under the active Stage 3.4 contract;
- originals already stored remain preserved and unmodified;
- multi-file member failure preserves existing aggregate non-readiness behavior;
  and
- Register is never executed, including after failure.

No retry, compensation, rollback engine, recovery workflow, timeout, cleanup
expansion, transaction, or duplicate/idempotency semantics may be added.
