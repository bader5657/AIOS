# Failure Contract

The focused evidence must preserve the existing mixed contract exactly:

- Invalid RequestContext: no new validation contract; an existing type or
  attribute failure may propagate if upstream construction is bypassed.
- Storage failure: stops before Metadata and Manifest and returns the existing
  bounded non-success/readiness-false result.
- Metadata failure: propagates and prevents Manifest construction.
- Manifest failure: propagates, leaves no valid-looking completed Manifest,
  and cannot produce Register readiness.

No case adds retry, fallback, recovery orchestration, deletion of the stored
original, or downstream execution.
