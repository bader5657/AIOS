# AIOS Domain Foundation Master

## 1. Document Status

Status: Approved repository authority

Authority: Project Owner

Published scope: DF-03A.1, DF-03A.2A, DF-03B.1, DF-03C.1, DF-03D.1,
DF-03E.1A

This document is the repository source of truth for the Domain Foundation
contracts explicitly published below.

Anything marked **Not Yet Published** is not implementation authority.

This document does not modify the AIOS Blueprint or Frozen Roadmap.

---

## 2. Architectural Boundary

The domain foundation is located under:

`core/domain/`

The domain foundation must depend only on the Python standard library.

The domain foundation must not depend on:

- application services;
- adapters;
- Telegram;
- PostgreSQL;
- storage implementations;
- infrastructure;
- specialists;
- framework-specific code;
- concrete business domains.

Event Exposure is domain behavior owned by AggregateRoot. It exposes pending
DomainEvent instances only. It does not dispatch, publish, persist, serialize,
route, retry, or transport events, and it does not construct EventEnvelope
instances.

Allowed dependency direction:

```text
Concrete business domains
        ↓
core.domain
        ↓
Python standard library
Dependencies must never point from core.domain toward a concrete business
domain or infrastructure implementation.
3. Shared Domain Exceptions Contract
The published shared exception hierarchy is:
DomainError
├── DomainValidationError
└── DomainInvariantError
DomainError
DomainError is the base exception for failures originating from domain
behavior or domain rules.
It must inherit from Python's Exception.
DomainValidationError
DomainValidationError represents invalid domain input or invalid value
construction.
It must inherit from DomainError.
DomainInvariantError
DomainInvariantError represents an attempted operation that violates an
already established domain invariant.
It must inherit from DomainError.
Restrictions
The following exception is not part of the published foundation:
EntityNotFoundError
Missing-entity behavior belongs to a future repository contract and must not
be introduced during DF-03A.1.
4. Base Entity Contract
Purpose
Entity is the generic abstract base for domain objects whose continuity is
defined by identity.
Generic Identity
The base entity must support a generic identity type.
Conceptually:
Entity[EntityId]
The base class must not generate identities.
A concrete domain supplies the identity value.
Identity Property
The public identity property is named:
id
The identity must be provided during entity construction.
The identity must not be None.
Passing None as an identity must raise DomainValidationError.
Identity Immutability
An entity identity cannot be replaced after construction.
An attempt to assign a different value to id after construction must fail.
The implementation may enforce this using a read-only property, private
storage, or an equivalent standard-library mechanism.
Equality
Entity equality is identity-based.
Two entity instances are equal only when:
they are instances of the exact same concrete entity class; and
their identity values are equal.
Entities of different concrete classes are not equal, even if their identity
values are equal.
An entity compared with a non-entity value must not be equal.
Hashing
Entity hashing must be consistent with entity equality.
The hash must include:
the exact concrete entity class; and
the entity identity.
Conceptually:
hash((type(entity), entity.id))
Abstract Status
Entity must be an abstract base class and must not represent a concrete
business entity by itself.
Restrictions
The base entity must not contain:
persistence behavior;
serialization behavior;
event publication;
database identifiers generated internally;
Customer-specific behavior;
Conversation-specific behavior;
framework dependencies.
5. Base Value Object Contract
Purpose
ValueObject is the abstract base for domain concepts defined entirely by
their values rather than an independent identity.
Immutability
A value object must be technically immutable after construction.
The implementation must use Python standard-library enforcement.
Approved enforcement mechanism:
subclasses are immutable dataclasses using @dataclass(frozen=True); or
an equivalent standard-library mechanism that produces the same externally
observable immutability.
Documentation-only immutability is not sufficient.
Equality
Value object equality is value-based.
Two value objects are equal only when:
they are instances of the exact same concrete value-object class; and
all declared value components are equal.
Value objects of different concrete classes are not equal even when they hold
equivalent component values.
Hashing
A valid value object must be hashable.
Hashing must remain consistent with equality and must use the immutable value
components.
Validation
Concrete value objects may validate their own values during construction.
Invalid construction must raise DomainValidationError.
The base ValueObject must not define concrete business validation rules.
Abstract Status
ValueObject must be abstract and must not itself represent a concrete
business value.
Restrictions
The base value object must not contain:
persistence behavior;
database mapping;
JSON serialization policy;
framework validation;
Customer-specific fields;
Conversation-specific fields;
mutable collections exposed as internal state.
Aggregate Root
Purpose
AggregateRoot is the abstract base for an entity that is the consistency
boundary and public entry point of an aggregate.
Entity Inheritance
AggregateRoot must inherit from Entity and must preserve the complete
published Entity contract.
It must support the same generic identity type as Entity.
Conceptually:
AggregateRoot[EntityId]
Identity
AggregateRoot must not generate identities.
Identity must be supplied during construction and exposed through the
inherited id property.
The inherited identity validation, immutability, equality, and hashing rules
must remain unchanged.
Aggregate Boundary Marker
AggregateRoot is a structural domain marker.
It identifies which entity is the root of an aggregate boundary without
introducing concrete business behavior.
Abstract Status
AggregateRoot must be an abstract base class and must not itself represent a
concrete aggregate.
Domain Event Boundary
The DomainEvent and Base Event Envelope contracts are published below. The
Base Event Exposure contract is also published below.
AggregateRoot owns its private pending-event collection and the published
recording, inspection, pulling, and clearing behavior. It must not define
event dispatch, publication, persistence, serialization, routing, retry,
transport, or EventEnvelope construction behavior.
Restrictions
The base aggregate root must not contain:
persistence behavior;
repository behavior;
serialization behavior;
event dispatch, publication, persistence, routing, retry, or transport
behavior;
EventEnvelope construction or storage;
Customer-specific behavior;
Conversation-specific behavior;
framework dependencies.
Base Repository Contract
Purpose
Repository is the generic abstract interface for storing and retrieving
aggregate roots without defining a persistence implementation.
Generic Types
The base repository must support:
an aggregate-root type; and
the identity type used by that aggregate root.
Conceptually:
Repository[AggregateType, EntityId]
AggregateType must be bound to AggregateRoot.
Operations
The complete published base repository interface consists only of:
save(aggregate: AggregateType) -> None
get(entity_id: EntityId) -> AggregateType | None
exists(entity_id: EntityId) -> bool
delete(entity_id: EntityId) -> bool
list() -> tuple[AggregateType, ...]
All five published repository methods are synchronous.
Save
save accepts an aggregate root for creation or update.
The base interface must not prescribe how or where the aggregate is stored.
Get
get returns the aggregate root matching the supplied identity.
When no matching aggregate exists, get returns None.
The base repository must not introduce EntityNotFoundError.
Exists
exists returns True when an aggregate root matching the supplied identity
exists and False otherwise.
Delete
delete removes the aggregate root matching the supplied identity.
It returns True when an aggregate was removed and False when no matching
aggregate existed.
List
list returns all stored aggregate roots as an immutable tuple.
Abstract Status
Repository and all five published operations must be abstract.
The base repository must not contain storage state or a concrete
implementation.
Restrictions
The base repository must not contain:
business behavior;
persistence implementation;
PostgreSQL behavior;
ORM or SQLAlchemy behavior;
SQL behavior;
filesystem behavior;
infrastructure or adapter behavior;
framework dependencies;
Telegram behavior;
serialization behavior;
transaction behavior;
aggregate-specific queries;
Customer repository behavior;
Conversation repository behavior;
domain-event behavior.
Base DomainEvent Contract
Purpose
DomainEvent is the abstract base for an immutable domain record that
identifies a fact that occurred.
Required Identity
Every DomainEvent must have an identity exposed through:
id
The identity must be supplied during construction and must not be None.
The base DomainEvent must not generate identities.
Required Timestamp
Every DomainEvent must expose the timestamp at which the event occurred
through:
occurred_at
occurred_at must be supplied during construction.
occurred_at must be a timezone-aware datetime.
A datetime is timezone-aware only when its tzinfo is not None and its
utcoffset() is not None.
Passing None, a non-datetime value, or a naive datetime as occurred_at must
raise DomainValidationError.
Required Event Identifier
Every DomainEvent must expose its published event identifier through:
event_name
event_name must be supplied during construction.
event_name must be a string containing at least one non-whitespace character.
Blank and whitespace-only event names are forbidden.
Validation must use the event name after trimming leading and trailing
whitespace. The supplied event_name value remains unchanged when exposed.
Passing None, a non-string value, a blank string, or a whitespace-only string
as event_name must raise DomainValidationError.
Immutable Behavior
The event identity, occurred_at timestamp, and event_name cannot be replaced
after construction.
The implementation must enforce immutability using only Python
standard-library behavior.
Equality
DomainEvent equality is value-based across the complete published event
record.
Two domain events are equal only when:
they are instances of the exact same concrete DomainEvent class; and
their id values are equal; and
their occurred_at values are equal; and
their event_name values are equal.
Domain events of different concrete classes are not equal, even when all
three published field values are equal.
A domain event compared with a non-DomainEvent value must not be equal.
Hashing
Every valid DomainEvent must be hashable.
Hashing must be consistent with DomainEvent equality and must include:
the exact concrete DomainEvent class;
the id;
the occurred_at timestamp; and
the event_name.
Conceptually:
hash((type(event), event.id, event.occurred_at, event.event_name))
Abstract Status
DomainEvent must be abstract and must not itself represent a concrete domain
event.
Restrictions
The base DomainEvent must not contain:
AggregateRoot behavior;
Repository behavior;
Event Envelope behavior;
Event Exposure behavior;
Event Bus behavior;
infrastructure behavior;
persistence behavior;
serialization behavior;
framework dependencies;
Customer behavior;
Conversation behavior.
Base Event Envelope Contract
Purpose
EventEnvelope is the immutable, transport-neutral wrapper for one published
DomainEvent.
It adds no business behavior and must not mutate the wrapped DomainEvent.
Published Fields
The complete published EventEnvelope field set consists only of:
event
event_id
event_name
occurred_at
aggregate_id
correlation_id
causation_id
schema_version
Event
event must be supplied during construction.
event must be a DomainEvent instance and must not be None.
Passing None or a non-DomainEvent value as event must raise
DomainValidationError.
Mirrored Event Fields
event_id must exactly mirror event.id.
It must not be independently supplied or generated.
event_name must exactly mirror event.event_name.
It must not be independently supplied or normalized.
occurred_at must exactly mirror event.occurred_at and must remain
timezone-aware.
It must not be independently supplied or generated.
Aggregate Identity
aggregate_id is optional and may be None.
When supplied, it must be preserved without replacement after construction.
EventEnvelope must not perform aggregate lookup behavior.
Correlation Identity
correlation_id is optional and may be None.
When supplied, it must be preserved without replacement after construction.
Causation Identity
causation_id is optional and may be None.
When supplied, it must be preserved without replacement after construction.
Schema Version
schema_version is required.
It must be a positive integer with a value of at least 1.
It must be preserved without replacement after construction.
Zero, negative, and non-integer schema_version values must raise
DomainValidationError.
Immutability
EventEnvelope must be technically immutable.
No published field may be replaced after construction.
The implementation must enforce immutability using only Python
standard-library mechanisms.
Equality
EventEnvelope equality must include the exact concrete envelope type.
Two envelopes are equal only when they are instances of the exact same
concrete envelope class and these fields are equal:
event;
aggregate_id;
correlation_id;
causation_id; and
schema_version.
The mirrored event_id, event_name, and occurred_at fields are derived from
event and must not be counted a second time.
An EventEnvelope compared with a non-EventEnvelope value must not be equal.
Hashing
Every valid EventEnvelope must be hashable.
Hashing must use the exact concrete envelope type and the same fields used by
equality:
event;
aggregate_id;
correlation_id;
causation_id; and
schema_version.
Hashing must remain consistent with equality.
Conceptually:
hash((type(envelope), envelope.event, envelope.aggregate_id,
envelope.correlation_id, envelope.causation_id, envelope.schema_version))
Restrictions
EventEnvelope must not contain:
event bus behavior;
dispatcher behavior;
registry behavior;
handler behavior;
publisher behavior;
retry logic;
persistence behavior;
PostgreSQL behavior;
serialization implementation;
JSON conversion;
dictionary conversion;
transport protocol behavior;
Telegram behavior;
Customer behavior;
Conversation behavior;
infrastructure behavior;
framework dependencies;
automatic identity generation;
automatic correlation or causation generation;
automatic timestamp generation;
mutation of the wrapped DomainEvent.
Base Event Exposure Contract
Purpose
Base Event Exposure defines how an AggregateRoot records and exposes pending
DomainEvent instances before application or infrastructure code handles them.
Pending domain events are owned by the AggregateRoot that records them.
Event Exposure is domain behavior.
Ownership and Boundary
Event Exposure does not dispatch, publish, persist, serialize, route, retry,
or transport events.
Application or infrastructure code may retrieve events through the published
exposure API, but it may not mutate the aggregate's internal event collection
directly.
The internal pending-event collection must remain private.
Only DomainEvent instances may be recorded.
EventEnvelope is not stored inside AggregateRoot.
EventEnvelope construction remains outside Event Exposure.
Public API
The complete published Event Exposure public API consists only of:
record_event(event: DomainEvent) -> None
pending_events() -> tuple[DomainEvent, ...]
pull_events() -> tuple[DomainEvent, ...]
clear_events() -> None
No additional public Event Exposure method is published.
record_event
record_event accepts exactly one DomainEvent instance.
None and non-DomainEvent values are invalid and must raise
DomainValidationError.
record_event appends the event to the pending collection, preserves insertion
order, permits multiple events, and permits equal or duplicate events.
It returns None.
It does not wrap the event in EventEnvelope and does not dispatch or persist
the event.
pending_events
pending_events returns a snapshot of all currently pending events as an
immutable tuple in insertion order.
It does not remove or clear any event.
Repeated calls without mutation return equal tuples.
Callers cannot mutate the aggregate's internal collection through the
returned value.
pull_events
pull_events captures and returns a snapshot of all currently pending events as
an immutable tuple in insertion order, then clears the aggregate's pending
collection.
When no events are pending, it returns an empty tuple.
Calling pull_events twice without new events returns the prior events on the
first call and an empty tuple on the second call.
clear_events
clear_events removes all currently pending events and returns None.
It is safe when the collection is already empty.
It does not return the removed events and does not dispatch or persist events.
Initial State
A newly constructed AggregateRoot has no pending events.
pending_events initially returns an empty tuple.
pull_events initially returns an empty tuple.
clear_events on a new AggregateRoot succeeds without error.
Event Collection Rules
The internal collection is private and mutable only through the approved
AggregateRoot methods.
The internal collection may use a Python list or an equivalent
standard-library structure.
Public snapshots must always be tuples.
Events must remain in the exact order in which record_event received them.
Recording an event must not mutate that DomainEvent.
Clearing or pulling events must not mutate the DomainEvent instances.
No automatic EventEnvelope creation occurs.
No automatic ID, timestamp, correlation ID, causation ID, or schema version
generation occurs.
Implementation Authority
Event Exposure is behavior of:
core/domain/aggregate_root.py
AggregateRoot owns the pending-event collection and the four published public
operations.
The following separate module is not authorized:
core/domain/event_exposure.py
Restrictions
Event Exposure must not contain or introduce:
event bus;
dispatcher;
registry;
publisher;
handler execution;
retry logic;
event persistence;
outbox;
PostgreSQL;
serialization;
JSON or dictionary conversion;
EventEnvelope creation inside AggregateRoot;
transport protocols;
Telegram;
Customer behavior;
Conversation behavior;
adapters;
infrastructure;
framework dependencies;
asynchronous methods;
automatic event generation.
6. Published Domain Foundation Implementation Scope
The implementation authority currently published is:
core/domain/
├── exceptions.py
├── entity.py
├── value_object.py
├── aggregate_root.py
├── repository.py
├── domain_event.py
└── event_envelope.py
The matching unit-test scope is:
tests/unit/domain/
├── test_exceptions.py
├── test_entity.py
├── test_value_object.py
├── test_aggregate_root.py
├── test_event_exposure.py
├── test_repository.py
├── test_domain_event.py
└── test_event_envelope.py
Implementations may add required __init__.py package markers when necessary,
but those files must not expose unpublished contracts.
7. Required Published Contract Tests
Tests must verify at minimum:
Exceptions
DomainError inherits from Exception;
DomainValidationError inherits from DomainError;
DomainInvariantError inherits from DomainError;
exception messages are preserved.
Entity
identity is provided during construction;
None identity is rejected;
identity is publicly readable through id;
identity cannot be replaced;
same concrete type and same identity compare equal;
same concrete type and different identities compare unequal;
different concrete entity types with equal identities compare unequal;
entity compared with a non-entity value compares unequal;
equal entities produce equal hashes;
entities can be used as dictionary keys and set members;
the base entity does not generate identities.
Value Object
concrete value objects are immutable;
equal concrete value objects with equal components compare equal;
different component values compare unequal;
different concrete value-object types compare unequal;
equal value objects produce equal hashes;
value objects can be used as dictionary keys and set members;
invalid concrete value construction can raise
DomainValidationError;
the base class contains no Customer or Conversation behavior.
Required AggregateRoot Tests
Tests must verify at minimum:
AggregateRoot inherits from Entity;
identity is supplied during construction;
None identity is rejected through the Entity contract;
identity is publicly readable and cannot be replaced;
same concrete aggregate-root type and same identity compare equal;
same concrete aggregate-root type and different identities compare unequal;
different concrete aggregate-root types with equal identities compare
unequal;
equal aggregate roots produce equal hashes;
aggregate roots can be used as dictionary keys and set members;
the base aggregate root does not generate identities;
the base aggregate root exposes only the published Event Exposure
domain-event API;
the base aggregate root contains no Customer or Conversation behavior.
Required Event Exposure Tests
Tests in tests/unit/domain/test_event_exposure.py must verify at minimum:
a new AggregateRoot has no pending events;
pending_events() returns an empty tuple initially;
pull_events() returns an empty tuple initially;
clear_events() is safe on an empty aggregate;
record_event() accepts a DomainEvent;
record_event() returns None;
None is rejected with DomainValidationError;
non-DomainEvent values are rejected with DomainValidationError;
one event is exposed through pending_events();
multiple events preserve insertion order;
duplicate or equal events are permitted and preserved;
pending_events() returns a tuple;
pending_events() does not clear events;
the returned tuple cannot mutate internal state;
pull_events() returns all pending events as a tuple;
pull_events() preserves insertion order;
pull_events() clears pending events;
a second pull returns an empty tuple;
clear_events() removes all events;
clear_events() returns None;
new events can be recorded after pull_events();
new events can be recorded after clear_events();
recorded DomainEvent instances are not mutated;
EventEnvelope objects are not created or stored;
no event dispatch exists;
no event persistence exists;
no unpublished public API exists;
no prohibited dependency exists.
Required Repository Tests
Tests must verify at minimum:
Repository is generic over an AggregateRoot type and its identity type;
Repository is abstract;
save is abstract and accepts an aggregate root;
get is abstract and accepts an identity;
get permits None when no aggregate exists;
delete is abstract and accepts an identity;
delete reports whether an aggregate was removed;
the base repository contains no storage state or concrete persistence;
the base repository contains no aggregate-specific query;
the base repository contains no DomainEvent, Customer, or Conversation
behavior.
Required DomainEvent Tests
Tests must verify at minimum:
DomainEvent is abstract;
DomainEvent cannot be instantiated directly;
identity is required, supplied during construction, and publicly readable
through id;
None identity is rejected;
the base DomainEvent does not generate identities;
occurred_at is required, supplied during construction, and publicly readable;
None, non-datetime, and naive occurred_at values are rejected;
timezone-aware occurred_at values are accepted;
event_name is required, supplied during construction, and publicly readable;
None, non-string, blank, and whitespace-only event_name values are rejected;
id, occurred_at, and event_name cannot be replaced after construction;
same concrete event type with equal id, occurred_at, and event_name values
compares equal;
any unequal published field makes events of the same concrete type compare
unequal;
different concrete event types compare unequal even when all published field
values are equal;
a domain event compared with a non-DomainEvent value compares unequal;
equal domain events produce equal hashes;
domain events can be used as dictionary keys and set members;
the base DomainEvent contains no AggregateRoot or Repository behavior;
the base DomainEvent contains no Event Envelope, Event Exposure, Event Bus,
infrastructure, persistence, serialization, or framework behavior;
the base DomainEvent contains no Customer or Conversation behavior.
Required EventEnvelope Tests
Tests must verify at minimum:
EventEnvelope is immutable;
a valid DomainEvent is required;
None event is rejected;
a non-DomainEvent event is rejected;
event_id exactly mirrors event.id;
event_name exactly mirrors event.event_name;
occurred_at exactly mirrors event.occurred_at and remains timezone-aware;
optional aggregate_id is preserved;
optional correlation_id is preserved;
optional causation_id is preserved;
schema_version accepts positive integers;
zero schema_version is rejected;
negative schema_version is rejected;
non-integer schema_version is rejected;
equality follows the published exact-type and field rules;
hashing is consistent with equality;
no unpublished API exists;
no prohibited dependency exists.
8. Explicitly Unpublished Contracts
The following contracts exist in the approved architecture history but their
full approved text has not yet been published into this repository:
event dispatch;
event persistence;
Customer aggregate contract;
Customer repository contract;
Customer business rules contract;
Customer identity contract;
Customer name contract;
Customer address contract;
Customer city contract;
Conversation aggregate contract;
Conversation repository contract;
Conversation event contract;
Conversation business rules contract.
These items are marked:
Not Yet Published
They must not be reconstructed, inferred, or implemented from this document.
Their implementation requires a later Project Owner publication decision.
9. Current Restrictions
Until additional contracts are published, do not implement:
Customer;
Conversation;
event dispatch;
event persistence;
PostgreSQL domain mapping;
Telegram integration;
dependency injection;
infrastructure adapters.
10. Governance Rule
Published sections of this master document are implementation authority.
Unpublished sections are only a registry of missing authority.
When implementation behavior is not defined by a published section, stop and
report the missing authority instead of inventing behavior.
11. Change Control
Changes to this document require an explicit Project Owner decision.
Codex must not silently expand, reinterpret, or redesign the published
contracts.
