# Runtime API and Routing Evidence

The fresh runtime exposes `EventEngine`, synchronous
`register(event_name: str, handler: EventHandler) -> None`, and asynchronous
`process(envelope: EventEnvelope) -> EventDeliveryResult`.

`EventHandler` is equivalent to
`Callable[[EventEnvelope], Awaitable[None]]`. Routing reads only
`EventEnvelope.event_name`; no second routing vocabulary exists.
