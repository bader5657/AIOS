# Database, External Execution, and Infrastructure

Real disposable PostgreSQL is authorized only through
`AIOS_REGISTRY_TEST_DATABASE_URL`. The test must use an isolated disposable
database, schema, or container; apply the existing migration unchanged; avoid
production fallback and credentials; and clean up after execution.

- Production database: `PROHIBITED`
- Real Telegram: `NO`
- Production bot token: `PROHIBITED`
- External application network: `NO`
- URL retrieval: `NO`
- New infrastructure: `NONE`

Existing fake Telegram facilities, disposable PostgreSQL, Event Engine, and
AIOS Core are reused. No broker, queue, cache, vector database, LLM, or Ollama
is authorized.
