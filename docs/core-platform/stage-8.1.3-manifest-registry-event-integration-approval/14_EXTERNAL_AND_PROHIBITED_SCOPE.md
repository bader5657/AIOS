# External and Prohibited Scope

- Real Telegram: no
- External network: no, except connectivity to the approved disposable test DB
- Disposable PostgreSQL: yes, test-only
- Production DB: no
- New infrastructure: none

Prohibited work includes AIOS Core execution or changes, Brain/Intelligence,
Memory, Specialist Router, business consumers, Registry or Event Engine redesign,
schema or migration changes, persistence expansion, retry, broker, queue, Redis,
cache, vector database, LLM, deduplication, idempotency, compensation, distributed
transactions, and production execution.

Only fake/test asynchronous handlers may be used. No Core, Brain, Specialist, or
business handler is authorized.
