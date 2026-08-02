# Core Platform Stage 1.1.2 Baseline Inventory

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 1 — Main Step 1 — Sub Step 1.1.2 |
| Inventory baseline | `27e592af563fb116a102198f79d2f753763cadde` (`main`) |
| Inventory scope | Current platform packages, schemas, dependencies, and tests |
| Evidence method | Read-only inspection of the exact baseline tree and static source inventory |
| Prepared and reviewed by | Codex implementation agent |
| Review date | `2026-08-02` |
| Review status | Complete for Sub Step 1.1.2; no approval or progress claim inferred |

This inventory revalidates the EF-01 component inventory against the execution
baseline established by Sub Step 1.1.1. It records current-tree evidence only.
Historical branch files are not included as current implementation.

## Official Pipeline Mapping

| Blueprint-named capability | Current baseline evidence | Inventory state |
|---|---|---|
| Telegram Adapter boundary | `core/adapters/telegram/main.py` | Present; composes ingestion, Request Context, and Mission Control |
| Universal Ingestion | `core/ingestion/universal_ingestion.py` | Present |
| Request Context | `core/app/request_context.py`; `config/request-context.schema.json` | Runtime and schema present |
| Asset Pipeline | No `core/pipeline/` path in the baseline tree | Runtime absent |
| Document Manifest | `core/storage/document_manifest.py`; `config/ingestion-manifest.schema.json` | Runtime and schema present |
| PostgreSQL Registry | `docker/postgres/compose.yml`; `scripts/deploy-postgres.sh` | PostgreSQL deployment assets present; Registry runtime absent |
| AIOS Event Engine | `config/event-engine.schema.json` | Configuration present; runtime absent |
| AIOS Core boundary | No separately identifiable runtime package in the baseline tree | Absent as a named package/boundary |
| Input Classifier | `core/app/input_classifier.py` | Present |
| Original-file storage | `core/storage/file_storage.py`; `core/storage/telegram_storage.py` | Present |
| Metadata Engine | `core/storage/metadata_engine.py` | Present |
| Mission Control | `core/mission/status.py` | Present |

The presence statements above are inventory facts, not verification, contract
approval, completeness, or Roadmap progress claims.

## Current Package and Module Inventory

The baseline contains 32 tracked Python files under `core/`:

| Area | Tracked files | Current responsibility visible in source |
|---|---:|---|
| `core/` | 1 | Top-level package marker |
| `core/adapters/` | 3 | Adapter markers and Telegram polling/update boundary |
| `core/app/` | 3 | Input classification and Request Context |
| `core/domain/` shared | 7 | Domain primitives and exceptions; no `core/domain/__init__.py` is tracked |
| `core/domain/customer/` | 9 | Customer aggregate, value objects, events, factory, and repository contract |
| `core/ingestion/` | 2 | Universal Telegram ingestion result and orchestration |
| `core/mission/` | 2 | Mission status formatting |
| `core/storage/` | 5 | File/Telegram storage, metadata extraction, and document manifest |

Observed current internal dependency directions:

- `core.adapters.telegram` → `core.app`, `core.ingestion`, `core.mission`;
- `core.ingestion` → `core.app`, `core.storage`;
- `core.storage.telegram_storage` → `core.app.input_classifier` and
  `core.storage.file_storage`;
- `core.domain.customer` → shared `core.domain` contracts;
- shared `core.domain` → Python standard library and other shared domain
  modules only;
- no current import joins `core.domain` to the adapter/app/ingestion/storage
  implementation body.

## Schema and Configuration Inventory

| Path | Git blob at baseline | Declared surface |
|---|---|---|
| `config/request-context.schema.json` | `f637d7f7ad23c06830c8e6085895ace058e26cdb` | Request, source, user, input, context, routing, processing, and timestamps |
| `config/ingestion-manifest.schema.json` | `3e4606301bbe60ba6ce43b795a1a90d83779c506` | Document identity, source, classification, storage, processing, and timestamps |
| `config/event-engine.schema.json` | `b1c1e8365f6ce8beadca520f471991893474bcae` | Event names, publish/subscribe dispatch settings, retry, and consumers |

All three files are JSON configuration/example documents. They do not declare
the standard JSON Schema keywords needed to act as formal validation schemas.
Runtime/schema conformance and Event Engine behavior are not evaluated here.

PostgreSQL configuration is present at `docker/postgres/compose.yml` using
`postgres:17-alpine`, an external `aios-net` network, `.env`, a persistent data
mount, and `pg_isready`. `scripts/deploy-postgres.sh` validates and starts that
Compose configuration. No Registry persistence module or database client
dependency is present in the baseline.

## Dependency Inventory

`requirements.txt` pins 10 Python distributions:

| Distribution | Version | Observed baseline use |
|---|---:|---|
| `anyio` | `4.14.2` | No direct import in `core/`; dependency-chain support |
| `certifi` | `2026.6.17` | No direct import in `core/`; dependency-chain support |
| `h11` | `0.16.0` | No direct import in `core/`; dependency-chain support |
| `httpcore` | `1.0.9` | No direct import in `core/`; dependency-chain support |
| `httpx` | `0.28.1` | No direct import in `core/`; Telegram HTTP dependency chain |
| `idna` | `3.18` | No direct import in `core/`; dependency-chain support |
| `pillow` | `12.3.0` | Direct `PIL.Image` import in Metadata Engine |
| `python-dotenv` | `1.2.2` | Direct `dotenv.load_dotenv` import in Telegram Adapter |
| `python-telegram-bot` | `22.8` | Direct `telegram` imports in adapter, classifier, ingestion, and storage |
| `typing_extensions` | `4.16.0` | No direct import in `core/`; dependency-chain support |

The manifest does not label direct versus transitive dependencies; the table's
classification is based only on static imports in the baseline. There is no
separate development/test dependency manifest and no Python package/build
metadata in the tracked baseline. Runtime infrastructure additionally depends
on Docker Compose, PostgreSQL 17 Alpine, an externally created `aios-net`
network, and runtime environment files/secrets.

## Test Inventory

The baseline contains 16 tracked `test_*.py` modules, all beneath
`tests/unit/domain/`, plus `tests/unit/domain/customer/__init__.py`. Static
source inventory finds 212 declared `test_*` methods:

| Test area | Modules | Declared test methods |
|---|---:|---:|
| Shared Domain Foundation | 8 | 105 |
| Customer domain | 8 | 107 |
| Total | 16 | 212 |

Shared test modules cover aggregate root, domain event, entity, event envelope,
event exposure, exceptions, repository, and value object. Customer test modules
cover aggregate behavior, address, city, event factory, events, identity, name,
and repository contract.

No tracked tests cover `core/adapters`, `core/app`, `core/ingestion`,
`core/mission`, `core/storage`, the three configuration documents, PostgreSQL
deployment assets, or deployment scripts. This confirms EF-01's coverage and
root-discovery risks as inventory findings only. No test command is selected
and no functional result is claimed in this Sub Step; those belong to Main
Step 1.3.

## EF-01 Revalidation Result

Against baseline `27e592af563fb116a102198f79d2f753763cadde`, the EF-01 package,
schema, dependency-direction, missing-runtime, and test-coverage findings remain
materially accurate. Authority documents added after EF-01 do not add runtime
packages. Specifically:

- current Asset Pipeline, Registry, Event Engine runtime, and an identifiable
  AIOS Core package remain absent;
- the three configuration files remain present without corresponding full
  runtime coverage;
- the adapter/app/ingestion/storage/mission implementation remains untested;
- Domain Foundation and Customer remain the only areas with tracked tests; and
- historical branch implementations remain excluded from current-tree state.

## Review Boundaries and Result

This review creates no architecture, authority, approval, milestone, release,
version, or progress state. It does not evaluate historical component reuse,
define a root test command, run functional verification, or modify any
implementation.

**Sub Step 1.1.2 result: PASS**

Main Step 1.1 is complete. The next frozen-plan position is Stage 1, Main Step
1.2, Sub Step 1.2.1. That Sub Step is not started by this inventory.
