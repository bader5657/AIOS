# Dependency and Prohibited Scope

Allowed runtime dependencies are only:

- `core.domain.event_envelope.EventEnvelope`;
- Python standard-library `dataclasses` and `enum`; and
- AIOS Core-local result and enum types.

Static audit must prove absence of imports, calls, placeholders, and behavior
for Registry/PostgreSQL, Event Engine runtime/result/failure types, Brain,
Memory, Specialist Router, Specialists, Storage, Metadata, Manifest, business
features, external services, and infrastructure.

No persistence, retry, broker/network, queue, worker, Redis, vector database,
LLM/Ollama, HTTP service, Docker service, new third-party dependency, or
requirements change is authorized. No customer, order, product, finance,
content, intent, or specialist-selection semantics may appear.
