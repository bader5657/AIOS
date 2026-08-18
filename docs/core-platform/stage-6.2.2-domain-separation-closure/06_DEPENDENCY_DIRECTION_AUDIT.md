# Dependency Direction Audit

The only future runtime dependency direction approved by active authority is:

`core/event → core/domain`

The reverse direction is forbidden:

`core/domain ⇏ core/event`

Repository import/source audits found no `core.event`, Registry, Storage,
Pipeline, Ingestion, PostgreSQL, broker/client, Brain, or Specialist dependency
in `core/domain/`. No current `core/event/` runtime exists.

Future Event Engine may import active DomainEvent/EventEnvelope contracts. The
Domain Foundation must never import EventEngine, EventDeliveryResult, handler,
registration, or dispatch types.

**DEPENDENCY DIRECTION = PASS**
