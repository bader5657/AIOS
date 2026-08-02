# Core Platform Stage 1.2.3 Event Engine Disposition

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 1 — Main Step 1.2 — Sub Step 1.2.3 |
| Current review baseline | `25f949443317520343ed3bb9fb7c18e3de0357fa` (`main`) |
| Frozen-plan identifier | `c56e046` |
| Resolved historical commit | `c56e04669081e39de477f65d83415c729f15ca3d` |
| Historical commit subject | `feat(core-platform): add event engine foundation` |
| Historical branch evidence | `origin/sprint-18-conversation-engine` |
| Review method | Read-only source, test, configuration, dependency, and domain-boundary comparison |
| Component disposition | **ADAPT** |
| Review date | `2026-08-02` |

Git resolves the frozen plan's short identifier `c56e046` uniquely to the full
commit recorded above. The commit is not an ancestor of current `main` and is
not current implementation. This disposition does not copy, merge, approve, or
activate its content.

## Scope

This review covers only the Event Engine files introduced by commit `c56e046`:

| Historical path | Role |
|---|---|
| `core/event/__init__.py` | Package marker |
| `core/event/event.py` | Mutable payload event record with generated timestamp |
| `core/event/registry.py` | In-memory event-name-to-handler registry |
| `core/event/dispatcher.py` | Synchronous sequential handler dispatch |
| `tests/unit/event/__init__.py` | Test package marker |
| `tests/unit/event/test_event.py` | Event construction and blank-value tests |
| `tests/unit/event/test_registry.py` | Handler registration and unknown-event tests |
| `tests/unit/event/test_dispatcher.py` | Successful and unknown-event dispatch tests |

Asset Pipeline, PostgreSQL Registry, AIOS Core, and all later implementation
or verification work are excluded.

## Current Authority Used for Comparison

The active Blueprint places AIOS Event Engine after PostgreSQL Registry and
before AIOS Core. Current `config/event-engine.schema.json` names a
publish/subscribe mode, retry enabled with maximum three attempts, event names,
and downstream consumers. The configuration is evidence, not an approved
runtime behavior contract.

The approved Domain Foundation establishes these current boundaries:

- `DomainEvent` is an immutable, abstract domain fact with identity,
  timezone-aware occurrence time, and event name;
- `EventEnvelope` is an immutable, transport-neutral wrapper that mirrors the
  domain event and carries aggregate, correlation, causation, and schema
  version values;
- neither `DomainEvent` nor `EventEnvelope` may contain event bus, dispatcher,
  registry, handler, retry, persistence, or transport behavior;
- AggregateRoot event exposure records and returns `DomainEvent` instances but
  does not dispatch, publish, persist, serialize, route, retry, or transport
  them; and
- envelope construction and all Event Engine behavior remain outside the
  Domain Foundation.

The frozen Execution Plan reserves Event Engine contract, registration,
dispatch, retry, failure, integration, and verification decisions for Stage 6.
No approved Stage 6 engine contract exists at the current review baseline, so
this review does not invent those semantics.

## Evidence Comparison

| Historical behavior | Current authority/baseline comparison | Finding |
|---|---|---|
| Defines a separate `Event` with `event_id`, `event_name`, `payload`, and generated `created_at` | Does not consume current `DomainEvent` or `EventEnvelope`; duplicates event identity/time concepts | Historical `Event` model must not be reused |
| Uses `datetime.utcnow()` | Generates a timezone-naive timestamp, conflicting with current timezone-aware `DomainEvent.occurred_at` | Reject timestamp behavior |
| Stores a mutable payload dictionary in a non-frozen dataclass | Does not meet current immutable domain/envelope boundary | Reject model behavior |
| Raises built-in `ValueError` for blank identifiers/names | Current domain boundary uses `DomainValidationError` and requires explicit typed construction | Not compatible as a domain event contract |
| `EventRegistry` appends synchronous handlers by event name | Provides a minimal handler-registry structural concept outside Domain Foundation | Candidate for adaptation only |
| `get_handlers()` returns a copied list | Avoids direct mutation of the internal list, but no registration validation or lifecycle is defined | Partial evidence only |
| `EventDispatcher` invokes handlers sequentially | Provides minimal dispatch ordering evidence | Candidate for adaptation only |
| Unknown events silently invoke no handler | Behavior exists, but no current authority approves silent handling | Unresolved; cannot adopt |
| No handler exception isolation, retry, duplicate, idempotency, or failure policy | Does not implement configuration retry evidence or Stage 6 verification needs | Must adapt after contract approval |
| No PostgreSQL Registry output or AIOS Core input integration | Does not satisfy either side of the official pipeline position | Incomplete |
| Seven historical tests cover only construction, registration, happy dispatch, and unknown names | No DomainEvent/EventEnvelope compatibility, retry, handler failure, duplicate, isolation, or integration coverage | Insufficient for reuse |
| Tests import pytest for exception assertions | No pytest dependency is pinned in historical/current `requirements.txt` | Tests cannot be adopted blindly |

Static search found no reference to `core.domain`, `DomainEvent`,
`EventEnvelope`, retry, failure handling, schema version, correlation, or
causation in the historical Event Engine source or tests. The historical and
current Event Engine configuration and `requirements.txt` are identical.

## Disposition

**ADAPT** only the historical handler-registry and sequential-dispatch concepts
as evidence for later Stage 6 contract review.

Eligible evidence to carry forward:

- an application/infrastructure package separate from Domain Foundation;
- event-name-to-handler registration as a historical structural candidate;
- defensive copying of the handler list; and
- deterministic registration-order dispatch as a historical behavior
  candidate.

Not accepted for direct reuse:

- the historical `Event` class, payload model, identifier, or timestamp logic;
- any conversion between `DomainEvent`, `EventEnvelope`, and engine input;
- handler type/API, silent unknown-event behavior, or synchronous-only policy;
- retry, failure, duplicate, isolation, idempotency, or persistence semantics;
- configured consumer behavior, including Brain or Specialist implementation;
- the historical tests as sufficient verification; and
- the historical package as current or approved runtime.

Future adaptation depends on verified PostgreSQL Registry output and approved
Stage 6.1/6.2 contracts that preserve the Domain Foundation boundary. Resolving
those dependencies now would exceed Sub Step 1.2.3, so none is implemented.

## Reference Integrity Finding

Some pre-existing untracked EF-01/EF-02 text expands `c56e046` to
`c56e04669081e39f6f8709da0c4652a332083c1`, which Git cannot resolve. EF-03
records the resolvable full commit
`c56e04669081e39de477f65d83415c729f15ca3d`, and Git uniquely resolves the
frozen plan's required short identifier to that same commit. The untracked
documents and frozen plan are not changed; this finding does not block the
commit-specific review.

## Validation and Result

Review evidence was obtained with read-only Git inspection of identifier
resolution, commit metadata, the complete historical patch, all eight
historical files, current-tree absence, branch containment, current Event
Engine configuration, dependencies, and the current `DomainEvent`,
`EventEnvelope`, and AggregateRoot exposure contracts.

No historical file was copied or merged. No source, test, dependency, schema,
domain, runtime, authority, milestone, freeze, or product-status artifact was
changed.

**Sub Step 1.2.3 result: PASS**

Main Step 1.2 is complete. The next frozen-plan position is Stage 1, Main Step
1.3, Sub Step 1.3.1. That Sub Step is not started by this disposition.
