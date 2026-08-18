# Baseline and Authority Trace

## Git baseline

At package creation, `HEAD`, local `main`, and `origin/main` all resolved to
`f5f21d93bb121119d8ff5b2688600fcde2086b8b`; the worktree was clean. That
commit is the accepted Stage 6.1.1 baseline and contains the merged Stage 5.4.1
verification closure. Open PR #1 is unrelated historical branch evidence and
does not alter this baseline.

## Authority order applied

1. `docs/AIOS_ARCHITECTURE_v1.md` — official component and lifecycle order.
2. `docs/AIOS_Roadmap_Frozen.md` — Core Platform scope boundary.
3. `docs/architecture/AIOS_AUTHORITY_HIERARCHY.md` — authority precedence.
4. `docs/architecture/AIOS_CANONICAL_MODEL.md` — canonical `DomainEvent` and
   `EventEnvelope` meaning.
5. `docs/architecture/AIOS_LAYER_ARCHITECTURE.md` — narrow Process handoff.
6. `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — exact event
   and envelope contracts.
7. `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md` — Event Engine owns
   Process, bounded input/output, and stop boundary.
8. `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1.md` — Stage 6.1.1 name,
   purpose, evidence, and later-stage reservations.
9. Stage 5.4.1 approval and closure records — completed upstream handoff.
10. Project Owner decisions recorded in this package.

The Project Owner decisions reconcile previously unresolved producer,
consumer, and envelope-construction ownership narrowly for Stage 6.1.1. They
do not amend Blueprint, Frozen Roadmap, Domain Foundation, or Layer
Architecture documents.
