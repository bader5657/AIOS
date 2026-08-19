# Prohibited Scope and Review

Verification must statically confirm that Adapter does not classify, store, or
construct RequestContext; Asset Pipeline does not construct RequestContext;
Registry does not create DomainEvent; Event Engine does not invoke Core; Core
does not invoke Brain; and Respond does not reinterpret Event, Core, Brain, or
business semantics.

Prohibited scope includes Brain/Intelligence, Memory, Specialist Router,
business behavior, LLM/Ollama, retry, broker/queue, new persistence semantics,
schema or migration changes, architecture redesign, production deployment, and
Stage 3–7 contract changes.

Review must reject over-mocking that fails to prove the real lifecycle order,
PostgreSQL commit visibility, or actual Event Engine/Core handoff.
