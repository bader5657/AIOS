# Idempotency, Actor Provenance, and Activation Boundary

## Current duplicate behavior

The current `material_receipts.source_asset_reference` is indexed but is not
unique. Receipt IDs are application-generated UUIDv4 values. Consequently,
repeated Stage 0.31B invocations for the same retained manifest and facts can
create independently identified candidates.

This is not runtime idempotency. It is accepted only for isolated,
non-activated Stage 0.31B implementation and testing so that composition can be
verified without inventing an ungoverned business rule or schema migration.

Before production activation, separate governance must define and prove atomic
source-level deduplication. The recommended future v1 rule is:

> At most one active material-receipt candidate exists per retained manifest,
> where active means neither `REJECTED` nor `CANCELLED`.

Replacement and correction flows require separate governance. This package
does not authorize an application-only check, uniqueness constraint, partial
index, schema migration, or other deduplication mechanism.

## Actor provenance

The initial two-input API does not accept `ActorContext`. The present schema has
no durable candidate-creation actor field. Accepting and validating an actor
without durable recording would overstate the audit guarantee.

Durable candidate-creation actor provenance is a mandatory production-activation
gate and requires separate governance. A future governed solution may use a
schema field, audit event, or separate authoritative audit record, but none is
selected or authorized here. Any future actor grammar should reuse the Stage
0.30 `ActorContext` rather than create a competing identity grammar, unless a
later governance decision explicitly states otherwise.

Actor provenance grants no confirmation or posting authority.

## Initial implementation authority boundary

A later implementation authorization may permit only:

- a create-only Stage 0.31B use case and port;
- a narrow, stateless create-only adapter;
- an outer test composition;
- bounded orchestration errors/results where demonstrably needed;
- unit tests;
- fresh admitted disposable PostgreSQL integration tests; and
- security/object-graph tests.

It may not permit Telegram or Universal Ingestion runtime changes, schema
migrations, systemd/service changes, production activation, confirmation,
posting, stock mutation, movement creation, inference invocation, production
database contact, or production credential creation.

## Error boundary

Any later orchestration error boundary must preserve useful bounded Stage 0.31A
and Stage 0.30 reason information without exposing SQL, DSN, credentials,
Psycopg internals, traceback detail, raw manifest contents, or filesystem detail
beyond approved source identity. A new taxonomy is allowed only if needed for
bounded orchestration; it must not turn internal objects into public authority.

## Production activation separation

Implementation and test composition are distinct from production activation.
Even after a successful Stage 0.31B implementation merge, the following remain
unauthorized:

- `aios.service` startup wiring;
- Telegram handlers, tokens, configuration, or setup;
- `ingest_telegram_message` changes;
- Universal Ingestion callbacks;
- event-router wiring; and
- any automatic candidate creation.

A separate activation governance stage is mandatory. At minimum it must close:

1. atomic source-manifest idempotency/deduplication;
2. durable candidate-creation actor provenance;
3. activation and runtime-secret safety; and
4. an explicit production safety review.

Existing Telegram integration and Universal Ingestion remain unchanged. Future
activation may extend the existing path only under separate approval; it must
not repeat Telegram setup. OCR, Vision, LLM, and Brain remain without
receipt-fact authority.

## Technical debt posture

Numeric upper-bound technical debt is CLOSED. These posting-related items remain
nonblocking while confirmation and posting are unreachable:

- simultaneous successful-posting concurrency coverage;
- deeper `ALREADY_POSTED`/current-stock/history reconciliation; and
- chained Psycopg cause hardening.

Source-manifest candidate idempotency and durable creation actor provenance are
not blockers for isolated Stage 0.31B composition implementation, but both are
blocking gates for production activation.
