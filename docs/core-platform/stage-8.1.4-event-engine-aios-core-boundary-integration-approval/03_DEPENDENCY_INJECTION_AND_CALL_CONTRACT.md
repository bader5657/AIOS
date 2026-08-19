# Dependency Injection and Call Contract

The existing Universal Ingestion entrypoint may add exactly one optional,
keyword-only dependency in repository-conformant form:

```python
aios_core: AIOSCore | None = None
```

It must preserve compatibility for callers that do not request Route. There is
no global singleton, implicit construction, environment/config factory, service
locator, Brain dependency, or hidden default Core instance.

When an approved DomainEvent is supplied and Event Engine delivery succeeds,
an injected `aios_core` is required before Route can execute. The exact
missing-dependency disposition must follow the existing explicit-dependency
pattern used for `event_engine`: raise a direct `ValueError` rather than
constructing a hidden dependency or falsely claiming readiness.

The sole approved invocation is:

```python
core_route_result = await aios_core.route(envelope)
```

No alias, second call, retry, task creation, gather, queue, or background work
is authorized.
