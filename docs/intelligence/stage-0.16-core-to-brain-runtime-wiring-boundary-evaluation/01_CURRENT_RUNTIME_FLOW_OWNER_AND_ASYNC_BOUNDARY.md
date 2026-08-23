# Current Runtime Flow, Owner, and Async Boundary

## Actual service and adapter flow

`aios.service` starts one process with:

`/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`

`core/adapters/telegram/main.py` constructs the Telegram `Application`,
registers async handlers, and enters `run_polling()`. `handle_update()` awaits
`ingest_telegram_message()`. The Telegram framework owns the running event loop;
the request path is already native async and must continue with `await`, never
with nested `asyncio.run`, blocking calls, or hidden thread pools.

The production adapter supplies no `domain_event`, `event_engine`, or
`aios_core`. Therefore current production execution performs recognition,
RequestContext creation, asset-pipeline work, and Registry registration, but it
does not publish an event or call `AIOSCore.route()`.

## Repository route flow and stop point

When tests or a future composition explicitly supply all three dependencies,
`core/ingestion/universal_ingestion.py` owns this sequence:

`RequestContext → asset pipeline → Registry → EventEnvelope → EventEngine.process() → AIOSCore.route()`

`AIOSCore.route()` produces the exact `CoreRouteResult`. Universal Ingestion
then computes only the boolean `route_handoff_ready` when the result is
successful and targets `AIOS_BRAIN_BOUNDARY`. It discards the result at return
and invokes no mapper or Brain receiver. This is the exact current stop point.

No explicit Brain continuation hook or port exists. The smallest existing
orchestration seam is immediately after `await aios_core.route(envelope)` in
Universal Ingestion. `AIOSCore` itself is a stateless router and should remain
unchanged. Telegram, Mapper, Receiver, provider adapter, Domain, Registry, and
Event Engine internals are not wiring owners.
