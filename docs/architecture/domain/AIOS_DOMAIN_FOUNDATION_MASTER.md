# AIOS Domain Foundation Master

## 1. Document Status

Status: Approved repository authority

Authority: Project Owner

Published scope: DF-03A.1, DF-03A.2A, DF-03B.1, DF-03C.1, DF-03D.1,
DF-03E.1A, and the DF-04 Customer Domain contract through DF-04.5

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
6. Customer Identity Contract
Purpose
CustomerId is the identity type of the Customer aggregate.
Type and Value
CustomerId is an immutable ValueObject wrapping exactly one Python str value.
The underlying public value is named:
value
CustomerId must inherit from the published ValueObject foundation.
CustomerId must not inherit from Entity.
The CustomerId value must be supplied externally. CustomerId must not
generate identifiers automatically.
Validation
The value:
- must be a str;
- must not be empty;
- must not contain only whitespace; and
- must not have leading or trailing whitespace.
Leading and trailing whitespace must not be silently trimmed.
Invalid construction must raise DomainValidationError.
Immutability
CustomerId must be technically immutable after construction.
Equality and Hashing
Equality is value-based and includes the exact concrete ValueObject type.
Two CustomerId instances are equal when their string values are equal.
Hashing must use the same concrete type and value and must remain consistent
with equality.
Public API
CustomerId exposes exactly one public property:
value
No additional public behavior is authorized.
Restrictions
The Customer Identity contract must not contain or introduce:
- UUID dependencies;
- automatic identifier generation;
- database sequence generation;
- database behavior;
- persistence mapping;
- serialization;
- Customer aggregate behavior;
- repository behavior;
- event behavior; or
- framework dependencies.
7. Customer Domain Contract
DF-04 Objective
DF-04 publishes the complete Customer Domain contract: Customer value objects,
the Customer aggregate and business rules, Customer domain events and event
exposure, and the CustomerRepository interface. This is domain authority only.
Customer Value Objects
CustomerName, CustomerAddress, and CustomerCity are immutable ValueObjects,
each wrapping exactly one public str property: value. Each value must be a str,
not empty or whitespace-only, and have no leading or trailing whitespace.
CustomerName and CustomerCity require at least 2 characters; CustomerAddress
requires at least 5. Values are not trimmed or normalized. Invalid construction
raises DomainValidationError. Equality and hashing follow ValueObject.
Implementation and test authority:
- core/domain/customer/customer_name.py
- tests/unit/domain/customer/test_customer_name.py
- core/domain/customer/customer_address.py
- tests/unit/domain/customer/test_customer_address.py
- core/domain/customer/customer_city.py
- tests/unit/domain/customer/test_customer_city.py
Customer Aggregate
Customer is an AggregateRoot with identity type CustomerId. Required state:
- id: CustomerId
- name: CustomerName
- address: CustomerAddress
- city: CustomerCity
- notes: str | None
All except notes are required. Notes default to None; when supplied they must
be str. Empty notes are allowed and preserved verbatim. Identity is not
generated. Invalid input raises DomainValidationError. Public read-only
properties are id, name, address, city, and notes. Approved operations:
- change_name(name: CustomerName) -> None
- change_address(address: CustomerAddress) -> None
- change_city(city: CustomerCity) -> None
- change_notes(notes: str | None) -> None
Exact required ValueObject types must be supplied; None is invalid for name,
address, and city. Notes may be None. Equal assignment is allowed, changes no
state, and records no event. Unequal updates change only the matching field,
preserve identity, and record the matching event after the state change. No
lifecycle/status, delete, deactivate, archive, merge, or restore behavior is
published. Equality and hashing use inherited identity semantics.
Implementation authority: core/domain/customer/customer.py
Test authority: tests/unit/domain/customer/test_customer.py
Customer Business Rules
- CustomerId is required and immutable.
- name, address, and city are required; notes are optional.
- duplicate names, addresses, and cities are allowed.
- the aggregate enforces no uniqueness.
- no Customer lifecycle/status exists in DF-04.
- domain objects perform no database or cross-Customer lookup.
Customer Domain Events
Exactly CustomerCreated, CustomerNameChanged, CustomerAddressChanged,
CustomerCityChanged, and CustomerNotesChanged are published by DF-04.4. No
other concrete Customer domain-event class is published.

All five classes inherit from the published DomainEvent foundation and remain
immutable domain records. Every constructor uses keyword-only parameters and
receives id, occurred_at, and event_name externally. A concrete event must not
generate an event ID, timestamp, or event name. The inherited DomainEvent
contract governs validation and immutability of id, occurred_at, and
event_name.

CustomerCreated

Exact event_name: customer.created

Constructor:

CustomerCreated(
    *,
    id,
    occurred_at,
    event_name,
    customer_id: CustomerId,
    name: CustomerName,
    address: CustomerAddress,
    city: CustomerCity,
    notes: str | None,
)

Payload fields are customer_id, name, address, city, and notes. customer_id
must be exactly CustomerId; name must be exactly CustomerName; address must be
exactly CustomerAddress; city must be exactly CustomerCity; and notes must be
str or None. Notes are preserved verbatim. Invalid payload values raise
DomainValidationError.

CustomerNameChanged

Exact event_name: customer.name_changed

Constructor:

CustomerNameChanged(
    *,
    id,
    occurred_at,
    event_name,
    customer_id: CustomerId,
    previous_name: CustomerName,
    new_name: CustomerName,
)

Payload fields are customer_id, previous_name, and new_name. customer_id must
be exactly CustomerId; previous_name and new_name must each be exactly
CustomerName; and previous_name and new_name must differ. Invalid payload
values raise DomainValidationError.

CustomerAddressChanged

Exact event_name: customer.address_changed

Constructor:

CustomerAddressChanged(
    *,
    id,
    occurred_at,
    event_name,
    customer_id: CustomerId,
    previous_address: CustomerAddress,
    new_address: CustomerAddress,
)

Payload fields are customer_id, previous_address, and new_address. customer_id
must be exactly CustomerId; previous_address and new_address must each be
exactly CustomerAddress; and previous_address and new_address must differ.
Invalid payload values raise DomainValidationError.

CustomerCityChanged

Exact event_name: customer.city_changed

Constructor:

CustomerCityChanged(
    *,
    id,
    occurred_at,
    event_name,
    customer_id: CustomerId,
    previous_city: CustomerCity,
    new_city: CustomerCity,
)

Payload fields are customer_id, previous_city, and new_city. customer_id must
be exactly CustomerId; previous_city and new_city must each be exactly
CustomerCity; and previous_city and new_city must differ. Invalid payload
values raise DomainValidationError.

CustomerNotesChanged

Exact event_name: customer.notes_changed

Constructor:

CustomerNotesChanged(
    *,
    id,
    occurred_at,
    event_name,
    customer_id: CustomerId,
    previous_notes: str | None,
    new_notes: str | None,
)

Payload fields are customer_id, previous_notes, and new_notes. customer_id must
be exactly CustomerId; previous_notes and new_notes must each be str or None;
and previous_notes and new_notes must differ. Note values are preserved
verbatim. Invalid payload values raise DomainValidationError.

For every concrete event, the externally supplied event_name must equal its
exact published value. A mismatch raises DomainValidationError; it must not be
silently replaced or normalized.

All base and payload fields are immutable after successful construction.
Concrete implementations may use private slots plus read-only properties or
another standard-library-only mechanism with equivalent externally observable
immutability. No payload list, dictionary, or other mutable collection is
published.

Concrete Customer-event equality requires the exact same concrete event class,
equal inherited id, occurred_at, and event_name fields, and equal complete
concrete payload fields. Hashing uses the exact concrete event class, all
inherited equality fields, and all concrete payload equality fields. Equal
events have equal hashes. Events of different concrete classes are unequal
even when all comparable values otherwise match, and comparison with a
non-event value is unequal.

DF-04.4 publishes event record classes only. It does not publish an event
factory, ID generation, timestamp generation, Customer event recording
integration, automatic event creation, dispatch, an event bus, publication,
persistence, serialization, EventEnvelope creation, or infrastructure
dependencies. CustomerCreated construction integration remains deferred to
DF-04.5, and update-event integration remains deferred to DF-04.6. No factory
API or generation policy may be inferred.
Event implementation authority: core/domain/customer/events.py
Event test authority: tests/unit/domain/customer/test_customer_events.py
Customer Event Factory
DF-04.5 publishes CustomerEventFactory as a concrete, stateless class. It is
not an abstract base class or interface and has no subclasses or extension
contract.

Implementation authority:
core/domain/customer/event_factory.py

Test authority:
tests/unit/domain/customer/test_customer_event_factory.py

Construction
CustomerEventFactory() takes no arguments and creates no providers, values, or
mutable state. Positional or keyword constructor arguments are invalid and
raise TypeError. The class defines no custom equality or hashing behavior;
instances retain standard identity-based object equality and hashing.

Public API
The complete published public API consists only of these instance methods:

create_customer_created(
    *,
    id: object,
    occurred_at: datetime,
    customer_id: CustomerId,
    name: CustomerName,
    address: CustomerAddress,
    city: CustomerCity,
    notes: str | None,
) -> CustomerCreated

create_customer_name_changed(
    *,
    id: object,
    occurred_at: datetime,
    customer_id: CustomerId,
    previous_name: CustomerName,
    new_name: CustomerName,
) -> CustomerNameChanged

create_customer_address_changed(
    *,
    id: object,
    occurred_at: datetime,
    customer_id: CustomerId,
    previous_address: CustomerAddress,
    new_address: CustomerAddress,
) -> CustomerAddressChanged

create_customer_city_changed(
    *,
    id: object,
    occurred_at: datetime,
    customer_id: CustomerId,
    previous_city: CustomerCity,
    new_city: CustomerCity,
) -> CustomerCityChanged

create_customer_notes_changed(
    *,
    id: object,
    occurred_at: datetime,
    customer_id: CustomerId,
    previous_notes: str | None,
    new_notes: str | None,
) -> CustomerNotesChanged

Every parameter after self is keyword-only. Missing required parameters,
positional arguments, or unexpected parameters raise TypeError. Each method
returns exactly the concrete event type shown in its signature and maps to no
other event class.

Event Creation Policy
The caller owns and supplies id and occurred_at for every operation. The
factory must pass both values unchanged to the event constructor. The id type
is object: DF-04.5 publishes no narrower event-ID type, but None remains
invalid under DomainEvent. The occurred_at value must satisfy the published
DomainEvent timezone-aware datetime contract.

The caller does not supply event_name. CustomerEventFactory owns selection of
the exact published event_name and passes it to the matching constructor:
- create_customer_created uses customer.created;
- create_customer_name_changed uses customer.name_changed;
- create_customer_address_changed uses customer.address_changed;
- create_customer_city_changed uses customer.city_changed; and
- create_customer_notes_changed uses customer.notes_changed.

The factory does not generate, replace, derive, cache, or otherwise own id or
occurred_at. It owns only the fixed method-to-event_name mapping.

Validation and Normalization
CustomerEventFactory performs no duplicate validation. It delegates all base
field and payload validation to the matching concrete event constructor.
DomainValidationError from that constructor propagates unchanged. The factory
must not catch, replace, wrap, or translate that exception.

The factory must not trim, coerce, normalize, copy, substitute, or otherwise
transform any caller-supplied value. Every supplied value is passed unchanged
to the matching event constructor.

Aggregate Interaction
CustomerEventFactory creates and returns event objects only. It must not
receive a Customer or AggregateRoot, access Customer state, invoke Customer
behavior, call record_event, inspect or mutate pending events, or otherwise
perform event-recording integration.

Dependencies and Restrictions
DF-04.5 may import only Python standard-library types needed by the published
signatures and published Customer domain types. It must not introduce:
- UUID generation or any other event-ID generation;
- datetime.now(), datetime.utcnow(), or any current-time call;
- a clock, ID provider, timestamp provider, or dependency-injection contract;
- repositories, persistence, ORM, database access, or network access;
- serialization or deserialization;
- dispatch, publication, an event bus, or handler execution;
- EventEnvelope construction or storage;
- application, adapter, infrastructure, or framework dependencies; or
- mutable factory state, caching, registration, or configuration.

DF-04.5 and DF-04.6 Boundary
DF-04.5 owns only the stateless CustomerEventFactory contract, construction of
the five published Customer event records from explicit caller values, and
focused factory tests. It does not alter Customer or AggregateRoot and does
not integrate event recording.

DF-04.6 owns all Customer integration: how a Customer receives or accesses a
factory, when Customer construction requests CustomerCreated, when successful
unequal change operations request matching changed events, and when Customer
records returned events through AggregateRoot. No DF-04.6 dependency-wiring or
recording API is published by DF-04.5 and none may be inferred from this
factory contract.

DF-04.5 Completion Gate
DF-04.5 is complete only when:
- CustomerEventFactory exists only at its authorized source path;
- its constructor and five-method public API exactly match this contract;
- every method returns the exact mapped concrete Customer event;
- caller-supplied id, occurred_at, and payload values are preserved unchanged;
- the factory supplies only the exact mapped event_name;
- validation and DomainValidationError behavior remain delegated unchanged;
- no normalization, generation, aggregate interaction, recording, envelope,
  or prohibited dependency is present;
- the authorized focused tests pass;
- the full domain test suite passes;
- core and tests compile; and
- only the authorized factory source and factory test paths are modified by
  the implementation slice.

No Customer package-export change is authorized by DF-04.5.
Customer Event Exposure
Customer uses only AggregateRoot record_event, pending_events, pull_events,
and clear_events. No Customer-specific exposure API, dispatch, persistence,
EventEnvelope creation, publisher, or event bus is published.
CustomerRepository
CustomerRepository is an abstract Repository specialization for Customer and
CustomerId. It exposes exactly inherited save(customer), get(customer_id),
exists(customer_id), delete(customer_id), and list(), with inherited behavior.
It adds no find_by_name, search, pagination, database behavior, PostgreSQL or
in-memory implementation, uniqueness checks, or transactions.
Implementation authority: core/domain/customer/repository.py
Test authority: tests/unit/domain/customer/test_customer_repository.py
Customer Package Authority
core/domain/customer/__init__.py and tests/unit/domain/customer/__init__.py are
authorized. The public package exports only published Customer symbols.
8. Published Domain Foundation Implementation Scope
The implementation authority currently published is:
core/domain/
├── exceptions.py
├── entity.py
├── value_object.py
├── aggregate_root.py
├── repository.py
├── domain_event.py
├── event_envelope.py
└── customer/
    ├── __init__.py
    ├── customer_id.py
    ├── customer_name.py
    ├── customer_address.py
    ├── customer_city.py
    ├── customer.py
    ├── events.py
    ├── event_factory.py
    └── repository.py
The matching unit-test scope is:
tests/unit/domain/
├── test_exceptions.py
├── test_entity.py
├── test_value_object.py
├── test_aggregate_root.py
├── test_event_exposure.py
├── test_repository.py
├── test_domain_event.py
├── test_event_envelope.py
└── customer/
    ├── __init__.py
    ├── test_customer_id.py
    ├── test_customer_name.py
    ├── test_customer_address.py
    ├── test_customer_city.py
    ├── test_customer.py
    ├── test_customer_events.py
    ├── test_customer_event_factory.py
    └── test_customer_repository.py
Package markers must not expose unpublished contracts.
9. Required Published Contract Tests
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
Required CustomerId Tests
Tests in tests/unit/domain/customer/test_customer_id.py must verify at minimum:
CustomerId inherits from ValueObject and does not inherit from Entity;
construction requires exactly one externally supplied value;
value is a str and is publicly readable through the value property;
empty, whitespace-only, leading-whitespace, and trailing-whitespace values are
rejected with DomainValidationError;
invalid whitespace is not silently trimmed;
CustomerId is technically immutable after construction;
equal string values compare equal and different string values compare unequal;
a different concrete ValueObject type with the same string value compares
unequal;
equal CustomerId instances produce equal hashes;
CustomerId instances can be used as dictionary keys and set members;
CustomerId does not generate identifiers automatically;
CustomerId exposes exactly one public property, value;
no additional public behavior exists;
no prohibited dependency or behavior exists.
Required Customer Domain Tests
The authorized Customer tests must verify all published construction,
validation, immutability, exact-type, equality, hashing, read-only property,
update, same-value, identity-preservation, business-rule, event field, event
recording, event exposure, abstract repository specialization, inherited
repository API, package export, and prohibited-behavior requirements.
Required Customer Event Tests
Tests in tests/unit/domain/customer/test_customer_events.py must verify at
minimum:
exactly CustomerCreated, CustomerNameChanged, CustomerAddressChanged,
CustomerCityChanged, and CustomerNotesChanged are published as concrete
Customer event classes;
all five classes inherit from DomainEvent;
all five constructor signatures are exact and keyword-only;
the exact event_name mapping is CustomerCreated to customer.created,
CustomerNameChanged to customer.name_changed, CustomerAddressChanged to
customer.address_changed, CustomerCityChanged to customer.city_changed, and
CustomerNotesChanged to customer.notes_changed;
valid construction preserves all externally supplied base and payload fields;
customer_id, Customer name, Customer address, and Customer city payloads use
the exact required published types;
invalid payload values raise DomainValidationError;
each changed event requires its previous and new values to differ;
notes accept str or None and are preserved verbatim;
all inherited base and concrete payload fields are immutable;
equality includes the exact concrete event class, all inherited base fields,
and every concrete payload field;
any differing equality field makes events unequal;
equal events produce equal hashes;
events work as dictionary keys and set members;
different concrete event classes compare unequal;
comparison with a non-event value is unequal;
event IDs, timestamps, and event names are externally supplied and no
generation exists;
a mismatched event_name raises DomainValidationError and is not replaced or
normalized;
the Customer event module contains no factory or automatic event creation, and
no Customer event recording,
dispatch, event bus, publication, persistence, serialization, EventEnvelope
creation, infrastructure dependency, Customer construction integration, or
Customer update integration exists; and
only the Python standard library and published domain dependencies are
imported.
Required Customer Event Factory Tests
Tests in tests/unit/domain/customer/test_customer_event_factory.py must verify
at minimum:
- CustomerEventFactory is concrete and constructible with no arguments;
- constructor arguments are rejected;
- the exact five-method public API and keyword-only signatures;
- missing, positional, and unexpected method arguments are rejected;
- every method returns exactly its mapped concrete Customer event class;
- the exact method-to-event_name mapping;
- caller-supplied id, occurred_at, and payload objects are preserved unchanged;
- timezone-aware occurred_at values are accepted and invalid values propagate
  DomainValidationError from the event constructor;
- every invalid base or payload value produces the event constructor's
  DomainValidationError without wrapping or translation;
- no caller-supplied value is normalized, coerced, copied, or substituted;
- the factory has no mutable state and uses standard object identity equality;
- the factory does not access Customer or AggregateRoot and records no event;
- no ID or timestamp generation, current-time call, provider, repository,
  persistence, serialization, dispatch, EventEnvelope, infrastructure, ORM,
  network, database, caching, registration, or configuration exists; and
- only the Python standard library and published Customer domain dependencies
  are imported.
10. DF-04 Implementation and Completion
Mandatory implementation sequence:
- DF-04.1 CustomerId implementation
- DF-04.2 CustomerName, CustomerAddress, CustomerCity
- DF-04.3 Customer aggregate without event creation integration
- DF-04.4 Customer domain events (ready for implementation)
- DF-04.5 CustomerEventFactory
- DF-04.6 Customer event recording integration
- DF-04.7 CustomerRepository interface
- DF-04.8 Full Customer domain verification
- DF-04.9 Customer baseline commit
Each slice modifies only authorized files, runs focused tests and the full
domain suite, compiles core and tests, stops on missing authority, and does not
commit until its verification gate passes.
DF-04 is complete only when every published Customer value object, aggregate,
business rule, event, exposure behavior, repository interface, and package
export is implemented only in its authorized path; all required focused and
full-domain tests pass; core and tests compile; no prohibited behavior or
unpublished API is present; event creation and recording use explicitly
published event-factory authority; and the verified Customer baseline commit
is created. Until DF-04.5 passes, DF-04.6 and overall DF-04 completion
remain blocked.
11. Explicitly Unpublished Contracts
The following contracts exist in the approved architecture history but their
full approved text has not yet been published into this repository:
event dispatch;
event persistence;
Customer event-recording dependency and integration contract;
Conversation aggregate contract;
Conversation repository contract;
Conversation event contract;
Conversation business rules contract.
These items are marked:
Not Yet Published
They must not be reconstructed, inferred, or implemented from this document.
Their implementation requires a later Project Owner publication decision.
12. Current Restrictions
Do not implement outside the published Customer authority:
Conversation;
event dispatch;
event persistence;
PostgreSQL domain mapping;
Telegram integration;
dependency injection;
infrastructure adapters.
13. Governance Rule
Published sections of this master document are implementation authority.
Unpublished sections are only a registry of missing authority.
When implementation behavior is not defined by a published section, stop and
report the missing authority instead of inventing behavior.
14. Change Control
Changes to this document require an explicit Project Owner decision.
Codex must not silently expand, reinterpret, or redesign the published
contracts.
