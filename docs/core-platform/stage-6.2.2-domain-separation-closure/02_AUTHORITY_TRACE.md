# Authority Trace

Authority was applied in this order:

1. Blueprint official Event Engine position and Process lifecycle action.
2. Frozen Roadmap Core Platform scope.
3. Authority Hierarchy precedence.
4. Canonical Model definitions of `DomainEvent` and `EventEnvelope`.
5. Layer Architecture narrow Registry → Event Engine → AIOS Core position.
6. Execution Plan Stage 6.2.2 row.
7. Stage 6.1.1 active Event Engine boundary contract.
8. Stage 6.1.2 active REPLACE disposition.
9. Stage 6.2.1 active runtime contract.
10. Domain Foundation Master contracts for DomainEvent, EventEnvelope, and
    AggregateRoot Event Exposure.
11. Config and historical artifacts as non-authoritative evidence only.

The exact Execution Plan requirement is: Event Engine consumes exposed events
outside aggregate behavior; no Domain Foundation scope change; no dispatch or
persistence is added to AggregateRoot, DomainEvent, or EventEnvelope; required
evidence is a dependency and API audit.
