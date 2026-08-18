# Stage 5.4.1 Separation

Stage 5.3.2 tests PostgreSQL Registry independently.

It must not modify or wire Asset Pipeline, Universal Ingestion, Document
Manifest, Telegram Adapter, or another caller. Document Manifest → PostgreSQL
Registry runtime wiring and end-to-end Register lifecycle evidence remain
Stage 5.4.1.
