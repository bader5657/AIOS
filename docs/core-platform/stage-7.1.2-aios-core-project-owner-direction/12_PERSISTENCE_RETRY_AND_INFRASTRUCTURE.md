# Persistence, Retry, and Infrastructure Direction

- `AIOS CORE PERSISTENCE = NOT AUTHORIZED`.
- `AIOS CORE RETRY = NOT AUTHORIZED`.
- `NEW INFRASTRUCTURE = NONE`.

No PostgreSQL/schema/table/ORM, state store, cache, vector database, event log,
retry loop, backoff, automatic reroute, Redis, Kafka, RabbitMQ, NATS, Celery,
queue, worker, broker, LLM/Ollama, external service, or Docker service is
authorized. A later explicit call is a new operation, not an automatic retry.
