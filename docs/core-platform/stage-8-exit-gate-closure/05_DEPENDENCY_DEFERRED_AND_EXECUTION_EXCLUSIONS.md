# Dependency, Deferred Items, and Execution Exclusions

## Import/dependency result

Storage, Registry, Event Engine, AIOS Core, Domain Foundation, and Asset Pipeline prohibited reverse edges are zero. Python import cycles are zero. Active Stage 8 imports of Brain runtime, Memory, Specialist Router/Specialists, and official business-domain behavior are zero. Psycopg is Registry-local; EventDeliveryResult does not leak into AIOS Core; CoreRouteResult has only its approved minimal readiness projection.

## Accepted non-blocking items

- Telegram SDK coupling is `EXPLICITLY DEFERRED / ACCEPTED TECHNICAL DEBT`, limited exactly to Adapter, classifier, Universal Ingestion, Asset Pipeline, and Telegram Storage.
- `Adapter → core.mission.status` is `ACCEPTED EXISTING OUT-OF-PIPELINE BEHAVIOR`; it is not official-ingestion authority.
- Arbitrary partial-destination cleanup after arbitrary mid-copy failure is not guaranteed beyond the current Storage contract. Temporary-download cleanup remains verified.
- Three non-failing Domain `PytestCollectionWarning` findings for helper `TestEvent` classes with constructors remain non-blocking; they are not missed test failures.

## Production and later-phase exclusions

Verification used disposable PostgreSQL only. Production PostgreSQL, real Telegram, production bot tokens, external application network, and production Brain were unused. No broker, queue, Redis, Kafka, RabbitMQ, Celery, vector database, LLM runtime, or new persistence service was introduced.

Stage 8 introduced no Intelligence, Memory, Specialist Router, Specialists, business workflow, or Stage 9 operational behavior.

`LATER-PHASE EXCLUSION = PASS`
