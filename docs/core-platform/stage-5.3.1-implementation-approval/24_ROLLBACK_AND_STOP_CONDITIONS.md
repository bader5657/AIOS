# Rollback and Stop Conditions

Implementation stops and its scoped changes must be reverted if:

- original binary or unauthorized schema content appears;
- schema differs from the Active design;
- historical Registry or Registry Entry appears;
- an unapproved dependency/path/configuration appears;
- production connection or credential use occurs;
- Stage 4 runtime or Stage 5.4.1 caller wiring changes;
- retry, delete, upsert, merge, dedupe, or speculative indexing appears;
- isolated migration cannot be verified safely;
- required tests/audits fail; or
- completion requires authority outside this package.

Database cleanup is limited to the disposable environment authorization and
must never target valued/production data.
