# Stage 5.4.1 Integration Separation

Stage 5.3.1 creates an independently usable/testable Registry component only.
It must not modify or wire:

- `core/pipeline/asset_pipeline.py`;
- `core/ingestion/universal_ingestion.py`;
- Document Manifest runtime;
- Telegram adapter; or
- any Register handoff caller.

Document Manifest → PostgreSQL Registry caller wiring and end-to-end lifecycle
evidence belong to Stage 5.4.1.
