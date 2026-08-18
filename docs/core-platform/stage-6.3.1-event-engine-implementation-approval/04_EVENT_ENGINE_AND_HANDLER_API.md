# EventEngine and Handler API

The fresh runtime class is `EventEngine`. It owns only:

- explicit in-memory handler registration;
- exact `EventEnvelope.event_name` routing;
- defensive handler snapshot creation;
- sequential awaited handler invocation; and
- bounded EventDeliveryResult construction.

Approved handler type:

```python
EventHandler = Callable[[EventEnvelope], Awaitable[None]]
```

Handlers are runtime callables, not entities or persistent subscribers. No
abstract framework, protocol dependency, Service Locator, consumer database,
network subscriber, or dynamic import mechanism is approved.

Event Engine creates neither DomainEvent nor EventEnvelope and owns no business
semantics.
