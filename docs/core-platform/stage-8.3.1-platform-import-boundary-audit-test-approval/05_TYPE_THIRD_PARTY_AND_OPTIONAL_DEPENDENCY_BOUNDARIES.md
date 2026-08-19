# Type, Third-Party, and Optional Dependency Boundaries

The focused audit must preserve these type boundaries:

- Telegram types below Adapter are permitted only in the exact deferred paths;
- Psycopg types remain Registry-local;
- Registry persistence DTOs cross only the approved Ingestion→Registry edge;
- `EventDeliveryResult` remains an Ingestion-side execution gate and is never AIOS Core semantic input; and
- `CoreRouteResult` remains Core-local except for the existing minimal readiness projection.

Approved third-party use is repository-grounded: python-telegram-bot at the
accepted Telegram boundary, python-dotenv for Adapter configuration, Pillow for
Metadata, and Psycopg for Registry. The Stage 8 runtime must not acquire Redis,
Kafka, RabbitMQ, Celery, SQLAlchemy ORM, LLM SDK, vector database, or other
unapproved persistence/network client imports.

Optional dependency gates remain unchanged: Registry is needed only on an
eligible registration path, Event Engine only for caller-supplied DomainEvent
publication, and AIOS Core only after successful Event delivery.
