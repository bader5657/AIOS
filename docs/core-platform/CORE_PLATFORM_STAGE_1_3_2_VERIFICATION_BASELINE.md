# Core Platform Stage 1.3.2 Verification Baseline

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 1 — Main Step 1.3 — Sub Step 1.3.2 |
| Verification baseline | `48e9017c51bcd9892d8024ae4d33f4289d3149ca` (`main`) |
| Verification scope | Current functional and dependency-boundary results |
| Repository-root command | Accepted Sub Step 1.3.1 command |
| Verification date | `2026-08-02` |
| Result | **PASS with recorded coverage gaps** |

This report establishes pre-change verification evidence for the exact
baseline above. It does not advance Blueprint, Roadmap, milestone, release, or
product status and does not represent uncovered behavior as verified.

## Runtime Verification

The single repository-root command accepted in Sub Step 1.3.1 was run without
modification:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v
```

Observed result:

```text
Ran 212 tests in 0.026s

OK
```

The command discovered the complete expected baseline inventory of 16 test
modules and 212 test methods. All tests passed, with no errors, failures, or
skips. No Python bytecode directory was created.

## Functional Baseline

| Area | Modules | Tests | Result | Verified boundary |
|---|---:|---:|---|---|
| Shared Domain Foundation | 8 | 105 | PASS | Entity, Value Object, Aggregate Root, Repository, Domain Event, Event Envelope, exceptions, and aggregate event exposure |
| Customer domain | 8 | 107 | PASS | Customer aggregate, value objects, five domain events, event factory, and repository specialization |
| Total | 16 | 212 | PASS | Current published Domain Foundation and Customer test surface only |

The passing result preserves the previously recorded 212-test Domain
Foundation baseline. It does not verify the official Core Platform path outside
the tested domain surface.

## Dependency-Boundary Baseline

The passing suite includes executable restrictions for the current domain
boundary. In particular, the tests confirm that:

- shared domain primitives contain no Customer or Conversation behavior;
- `AggregateRoot` event exposure does not create envelopes or add dispatch,
  persistence, transport, or other prohibited dependencies;
- `DomainEvent` and `EventEnvelope` expose no prohibited dependencies or
  behavior;
- the shared Repository contract contains no concrete storage or persistence;
- Customer value objects import only their permitted Domain Foundation
  dependencies;
- Customer events import only the standard library and published domain
  dependencies;
- Customer event-factory dependencies and implementation remain restricted;
- Customer aggregate behavior has no prohibited dependency; and
- Customer Repository remains a contract specialization without concrete
  persistence or prohibited imports.

A static import inventory of current `core/` source is consistent with those
passing assertions: shared `core.domain` imports only Python standard-library
and other shared domain modules, while `core.domain.customer` depends inward on
the published shared-domain contracts. No current domain source imports
adapter, app, ingestion, mission, storage, Telegram, database, or Event Engine
implementation modules.

This result applies only to dependency restrictions asserted by the existing
Domain Foundation and Customer tests. It is not a platform-wide dependency
audit and does not pre-empt the focused reviews required by later Sub Steps.

## Uncovered Current Packages and Assets

No tracked test targets the following present runtime packages:

| Current area | Present implementation | Baseline test coverage |
|---|---|---|
| `core.adapters` | Telegram adapter boundary | None |
| `core.app` | Input Classifier and Request Context | None |
| `core.ingestion` | Universal Ingestion | None |
| `core.mission` | Mission Control status | None |
| `core.storage` | file storage, Telegram storage, metadata, and manifest | None |

The current suite also does not verify:

- `config/request-context.schema.json`;
- `config/ingestion-manifest.schema.json`;
- `config/event-engine.schema.json`;
- `docker/postgres/compose.yml`; or
- `scripts/deploy-postgres.sh`.

Asset Pipeline, PostgreSQL Registry runtime, AIOS Event Engine runtime, and an
identifiable AIOS Core runtime boundary are absent at this baseline, so they
cannot be assigned current runtime test coverage. Their absence is retained as
an inventory fact, not treated as a failing test or resolved in this Sub Step.

## Scope Boundaries and Result

This Sub Step records only the current functional and dependency-boundary
results and the explicit uncovered-package inventory. It adds no source,
tests, dependencies, configuration, workflow, architecture, authority, gate,
or capability verification. In particular, it does not perform the focused
Telegram/Input Classifier or Mission Control work reserved for Main Step 1.4.

No Blueprint, Roadmap, Governance, `VERSION`, Domain Foundation, Execution
Plan, freeze document, milestone document, source, test, configuration,
database, deployment, or runtime file is changed.

**Sub Step 1.3.2 result: PASS**

Main Step 1.3 is complete. The next frozen-plan position is Stage 1, Main Step
1.4, Sub Step 1.4.1. That Sub Step is not started by this report.
