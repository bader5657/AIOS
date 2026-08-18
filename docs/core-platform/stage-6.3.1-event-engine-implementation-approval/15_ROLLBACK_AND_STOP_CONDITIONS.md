# Rollback and Stop Conditions

Implementation must stop and remain unapproved if:

- a Domain Foundation or Domain test modification is required;
- routing differs from exact `EventEnvelope.event_name`;
- `INVALID_ENVELOPE` is omitted or a fourth failure code is introduced;
- broker, persistence, retry, parallelism, config behavior, or new dependency
  appears;
- historical structure/API is restored;
- Stage 5, publisher integration, or an unlisted path must change;
- mandatory tests are skipped or fail; or
- dependency, prohibited-source, static, whitespace, or closed-world audit
  fails.

No corrective scope expansion may be assumed. Required new path/dependency
authority must be obtained before work continues.
