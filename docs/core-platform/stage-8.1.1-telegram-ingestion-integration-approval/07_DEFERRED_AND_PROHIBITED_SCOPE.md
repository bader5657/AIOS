# Deferred and Prohibited Scope

`MEDIA GROUP AGGREGATION = DEFERRED`. Telegram messages remain independent. No
buffer, correlation state, batching, timeout, queue, or state store is allowed.

`TELEGRAM SDK DECOUPLING BELOW ADAPTER = DEFERRED / SEPARATE AUTHORITY`.
Existing SDK coupling in classifier, Universal Ingestion, Asset Pipeline, and
Telegram Storage is not refactored here.

Web and approved YouTube URLs pass through unchanged. Universal Ingestion owns
recognition. No URL retrieval or network fetch is allowed.

Polling remains unchanged. Webhook, reverse proxy, and deployment topology are
deferred. Also prohibited: command redesign, new retry, business logic, Brain,
Memory, Specialist Router, n8n, Hermes/OpenClaw, Stage 5/6/7 redesign, and any
new Docker service, Redis, queue, database, LLM/Ollama, or infrastructure.
