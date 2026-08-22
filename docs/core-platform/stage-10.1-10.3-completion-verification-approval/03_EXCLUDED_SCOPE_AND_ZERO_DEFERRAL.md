# Excluded Scope and Zero-Deferral Gate

## Excluded-scope ledger method

Stage 10.1.2 must create a reviewed ledger with one row per excluded item,
category, source authority, exact rationale, owning later phase (when known),
and proof that the exclusion does not remove an Included Scope requirement.
Expected exclusions, subject to line-by-line authority confirmation, are:

- AIOS Brain execution, including Chief of Staff, Advisor, Decision Engine,
  Knowledge, and Planner behavior;
- Intelligence/LLM execution;
- AIOS Memory;
- Specialist Router and Specialists;
- business workflow/domain runtime and autonomous automation;
- n8n, Hermes, OpenClaw, and Ollama runtime;
- broker/queue infrastructure such as Redis, Kafka, RabbitMQ, or Celery;
- generalized retry, deduplication, idempotency, compensation, and arbitrary
  partial-destination cleanup beyond accepted component contracts;
- future interfaces, external integrations, and other Frozen Roadmap
  later-stage capabilities.

An expected item is not excluded merely because it appears above: Stage
10.1.2 must cite authority. Conversely, an Included Scope item cannot be
reclassified as excluded to obtain a pass.

## Hard gate

`INCLUDED_SCOPE_DEFERRED = 0`

An Included Scope requirement that is absent, incomplete, unverified, or lacks
accepted closure is completion-blocking. It must be corrected under separate
authority and reverified; it cannot be waived by this package.

Accepted Stage 8/9 findings may remain deferred only when authority proves
that they are outside Included Scope completion requirements or explicitly
accepted as non-blocking within the governing contract. Accepted technical
debt is not deferred required functionality.

Stage 10.1.2 passes only if the reviewed exclusion ledger is complete and the
hard-gate value is exactly zero.
