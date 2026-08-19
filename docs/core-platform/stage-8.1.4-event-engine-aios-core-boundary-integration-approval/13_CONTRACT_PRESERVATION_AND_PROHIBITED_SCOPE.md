# Contract Preservation and Prohibited Scope

Stage 8.1.4 consumes existing contracts unchanged. It must not modify:

- Event Engine runtime, API, handlers, result, or failure codes;
- AIOS Core `route` signature, result, target, failure code, statelessness, or determinism;
- EventEnvelope or DomainEvent;
- Registry runtime/result, transactions, migrations, or schema;
- Document Manifest, Storage, Metadata, Asset Pipeline, RequestContext, or adapter;
- configuration, dependencies, Blueprint, Frozen Roadmap, or architecture.

Brain/Intelligence, Memory, Specialist Router, Specialists, business logic,
persistence, response generation, LLM/Ollama, prompts, models, broker/queue,
network calls, retries, and production behavior remain prohibited.
