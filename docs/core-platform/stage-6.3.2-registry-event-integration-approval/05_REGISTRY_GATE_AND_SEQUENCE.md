# Registry Gate and Lifecycle Sequence

The exact sequence is:

`upstream success → Manifest complete → Registry commit succeeds → approved
DomainEvent present → EventEnvelope construction → await EventEngine.process()`

Registry output contributes only the successful-registration gate. No
`RegistryPersistenceRow` field is an event source. `record_id` remains
database-local and is not event identity, aggregate identity, correlation,
causation, payload, or routing input.

Registry failure causes zero envelope construction and zero Process calls.
