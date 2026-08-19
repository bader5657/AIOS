# Verification, Regression, and Exit Gates

The Stage 8.4.1 verification must pass with zero mandatory skips and prove:

- every mandatory failure and the unexpected Registry exception;
- the exact suppression and preservation matrices;
- real Registry rollback and committed-row preservation through Event/Core
  failures;
- Stage 6 semantics for `INVALID_ENVELOPE` without corrupting the conforming
  flow;
- Brain calls zero;
- retry, compensation, deduplication, and cross-component transactions absent;
- acknowledgement consequences and all false-success distinctions; and
- a closed-world one-test-file diff.

Unchanged regression evidence is required from Stages 8.1.1–8.3.1,
Storage/Metadata/Manifest, Registry, Event Engine, AIOS Core, Core Platform,
Domain, compile/static, dependency audit, prohibited-source audit, and
`git diff --check`.

Known unchanged capability-matrix baseline failures remain separately
classified as pre-existing and outside Stage 8.4.1.

Closure must resolve the Stage 8 exit-gate risks: false success, Respond
interpretation, failure containment, preservation, transaction isolation, and
absence of retry or compensation. This approval does not execute the exit gate.
