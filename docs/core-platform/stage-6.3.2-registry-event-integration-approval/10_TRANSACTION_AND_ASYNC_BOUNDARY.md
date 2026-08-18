# Transaction and Async Boundary

`PostgresRegistry.register()` completes its Registry-local transaction before
EventEnvelope construction and Event Engine execution. No SQL transaction
spans Process or handler execution; there is no distributed transaction.

Universal Ingestion is already async and directly awaits Process. Background
tasks, `asyncio.gather`, thread/process wrappers, broker delivery, and automatic
retry are prohibited.
