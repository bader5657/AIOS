# Ownership and Dependency Boundary

## Ownership

| Concern | Owner retained after this contract | Asset Pipeline authority |
|---|---|---|
| Transport receipt | Telegram Adapter boundary | None |
| Input recognition | Existing upstream classification authority | Consume result only |
| Ingestion acceptance/request | Universal Ingestion | Coordinate without override |
| Original persistence | Storage | Request and consume bounded result only |
| Metadata semantics/extraction | Metadata Engine under active Stage 3 authority | Request and carry result only |
| Document Manifest semantics/creation | Document Manifest boundary | Hand off inputs and consume disposition only |
| Register | PostgreSQL Registry boundary in Stage 5 | Expose existing readiness only; no execution |
| Business workflow/Intelligence | Later excluded layers | None |

Universal Ingestion remains responsible for its accepted receiving and
ingestion boundaries. Moving or delegating concrete call orchestration in a
later implementation does not transfer its semantic authority. The exact
runtime collaboration/API is deferred to scoped implementation approval.

## Allowed Dependency Boundary

Asset Pipeline is in Ingestion Layer. It may use only already-approved App and
Storage capabilities required by the active Request Context and Stage 3
contracts. Permission is narrow and does not mandate a dependency or authorize
a new general direction.

Any concrete import list must be closed by later implementation approval.

## Prohibited Dependencies and Regressions

- Pipeline → Registry;
- Pipeline → PostgreSQL, ORM, migration, transaction, or database service;
- Pipeline → Brain, Intelligence, AIOS Core downstream behavior, Event Engine,
  Specialist Router, Specialist, or business domain;
- Storage → App or any disguised replacement of that removed dependency;
- a new shared module created only to conceal an unauthorized dependency;
- historical package placement treated as authority; and
- any unapproved cross-layer direction.

This package grants no change to Layer Architecture.
