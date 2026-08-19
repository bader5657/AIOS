# Respond Acknowledgement Contract

`Respond` means the existing Telegram receipt/readiness acknowledgement only.
It is not a canonical Response object, Brain output, LLM output, business
completion, Event result, or Core route result.

The active Stage 8.1.1 gate is preserved exactly:

`register_handoff_ready == True`

Stage 8.2.1 may not replace this with `route_handoff_ready`, Event success, Core
success, or Brain readiness. The Adapter awaits the entire ingestion coroutine,
so the successful full trace proves Route completion before acknowledgement.
The payload remains unchanged and exposes no Registry record ID, Event failure
code, Core result, Brain output, or business semantics.

If focused evidence proves a semantic conflict with this authority, work stops
with `STAGE 8.2.1 RESPOND AUTHORITY CORRECTION REQUIRED`.
