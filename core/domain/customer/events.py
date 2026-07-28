"""Immutable Customer domain-event records."""

from __future__ import annotations

from datetime import datetime

from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName
from core.domain.domain_event import DomainEvent
from core.domain.exceptions import DomainValidationError


__all__ = (
    "CustomerCreated",
    "CustomerNameChanged",
    "CustomerAddressChanged",
    "CustomerCityChanged",
    "CustomerNotesChanged",
)


def _require_exact(value: object, expected_type: type, field: str) -> None:
    if type(value) is not expected_type:
        raise DomainValidationError(
            f"{field} must be exactly {expected_type.__name__}"
        )


def _require_notes(value: object, field: str) -> None:
    if value is not None and type(value) is not str:
        raise DomainValidationError(f"{field} must be a str or None")


class _CustomerEventRecord:
    __slots__ = ()

    _payload_fields: tuple[str, ...] = ()

    def _initialize_event(
        self,
        id: object,
        occurred_at: datetime,
        event_name: str,
        expected_event_name: str,
    ) -> None:
        if event_name != expected_event_name:
            raise DomainValidationError(
                f"event_name must be {expected_event_name!r}"
            )
        DomainEvent.__init__(self, id, occurred_at, event_name)

    def __setattr__(self, name: str, value: object) -> None:
        payload_slots = {
            slot
            for cls in type(self).__mro__
            for slot in getattr(cls, "__slots__", ())
            if isinstance(slot, str)
        }
        if name in payload_slots and hasattr(self, name):
            raise AttributeError(f"{name[1:]} cannot be changed")
        super().__setattr__(name, value)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        return DomainEvent.__eq__(self, other) and all(
            getattr(self, field) == getattr(other, field)
            for field in self._payload_fields
        )

    def __hash__(self) -> int:
        return hash(
            (
                type(self),
                self.id,
                self.occurred_at,
                self.event_name,
                *(getattr(self, field) for field in self._payload_fields),
            )
        )


class CustomerCreated(_CustomerEventRecord, DomainEvent):
    """Customer creation fact."""

    __slots__ = ("_customer_id", "_name", "_address", "_city", "_notes")
    _payload_fields = ("customer_id", "name", "address", "city", "notes")
    _EVENT_NAME = "customer.created"

    def __init__(
        self,
        *,
        id,
        occurred_at,
        event_name,
        customer_id: CustomerId,
        name: CustomerName,
        address: CustomerAddress,
        city: CustomerCity,
        notes: str | None,
    ) -> None:
        _require_exact(customer_id, CustomerId, "customer_id")
        _require_exact(name, CustomerName, "name")
        _require_exact(address, CustomerAddress, "address")
        _require_exact(city, CustomerCity, "city")
        _require_notes(notes, "notes")
        self._initialize_event(id, occurred_at, event_name, self._EVENT_NAME)
        self._customer_id = customer_id
        self._name = name
        self._address = address
        self._city = city
        self._notes = notes

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def name(self) -> CustomerName:
        return self._name

    @property
    def address(self) -> CustomerAddress:
        return self._address

    @property
    def city(self) -> CustomerCity:
        return self._city

    @property
    def notes(self) -> str | None:
        return self._notes


class CustomerNameChanged(_CustomerEventRecord, DomainEvent):
    """Customer name-change fact."""

    __slots__ = ("_customer_id", "_previous_name", "_new_name")
    _payload_fields = ("customer_id", "previous_name", "new_name")
    _EVENT_NAME = "customer.name_changed"

    def __init__(
        self,
        *,
        id,
        occurred_at,
        event_name,
        customer_id: CustomerId,
        previous_name: CustomerName,
        new_name: CustomerName,
    ) -> None:
        _require_exact(customer_id, CustomerId, "customer_id")
        _require_exact(previous_name, CustomerName, "previous_name")
        _require_exact(new_name, CustomerName, "new_name")
        if previous_name == new_name:
            raise DomainValidationError("previous_name and new_name must differ")
        self._initialize_event(id, occurred_at, event_name, self._EVENT_NAME)
        self._customer_id = customer_id
        self._previous_name = previous_name
        self._new_name = new_name

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def previous_name(self) -> CustomerName:
        return self._previous_name

    @property
    def new_name(self) -> CustomerName:
        return self._new_name


class CustomerAddressChanged(_CustomerEventRecord, DomainEvent):
    """Customer address-change fact."""

    __slots__ = ("_customer_id", "_previous_address", "_new_address")
    _payload_fields = ("customer_id", "previous_address", "new_address")
    _EVENT_NAME = "customer.address_changed"

    def __init__(
        self,
        *,
        id,
        occurred_at,
        event_name,
        customer_id: CustomerId,
        previous_address: CustomerAddress,
        new_address: CustomerAddress,
    ) -> None:
        _require_exact(customer_id, CustomerId, "customer_id")
        _require_exact(previous_address, CustomerAddress, "previous_address")
        _require_exact(new_address, CustomerAddress, "new_address")
        if previous_address == new_address:
            raise DomainValidationError(
                "previous_address and new_address must differ"
            )
        self._initialize_event(id, occurred_at, event_name, self._EVENT_NAME)
        self._customer_id = customer_id
        self._previous_address = previous_address
        self._new_address = new_address

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def previous_address(self) -> CustomerAddress:
        return self._previous_address

    @property
    def new_address(self) -> CustomerAddress:
        return self._new_address


class CustomerCityChanged(_CustomerEventRecord, DomainEvent):
    """Customer city-change fact."""

    __slots__ = ("_customer_id", "_previous_city", "_new_city")
    _payload_fields = ("customer_id", "previous_city", "new_city")
    _EVENT_NAME = "customer.city_changed"

    def __init__(
        self,
        *,
        id,
        occurred_at,
        event_name,
        customer_id: CustomerId,
        previous_city: CustomerCity,
        new_city: CustomerCity,
    ) -> None:
        _require_exact(customer_id, CustomerId, "customer_id")
        _require_exact(previous_city, CustomerCity, "previous_city")
        _require_exact(new_city, CustomerCity, "new_city")
        if previous_city == new_city:
            raise DomainValidationError("previous_city and new_city must differ")
        self._initialize_event(id, occurred_at, event_name, self._EVENT_NAME)
        self._customer_id = customer_id
        self._previous_city = previous_city
        self._new_city = new_city

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def previous_city(self) -> CustomerCity:
        return self._previous_city

    @property
    def new_city(self) -> CustomerCity:
        return self._new_city


class CustomerNotesChanged(_CustomerEventRecord, DomainEvent):
    """Customer notes-change fact."""

    __slots__ = ("_customer_id", "_previous_notes", "_new_notes")
    _payload_fields = ("customer_id", "previous_notes", "new_notes")
    _EVENT_NAME = "customer.notes_changed"

    def __init__(
        self,
        *,
        id,
        occurred_at,
        event_name,
        customer_id: CustomerId,
        previous_notes: str | None,
        new_notes: str | None,
    ) -> None:
        _require_exact(customer_id, CustomerId, "customer_id")
        _require_notes(previous_notes, "previous_notes")
        _require_notes(new_notes, "new_notes")
        if previous_notes == new_notes:
            raise DomainValidationError(
                "previous_notes and new_notes must differ"
            )
        self._initialize_event(id, occurred_at, event_name, self._EVENT_NAME)
        self._customer_id = customer_id
        self._previous_notes = previous_notes
        self._new_notes = new_notes

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def previous_notes(self) -> str | None:
        return self._previous_notes

    @property
    def new_notes(self) -> str | None:
        return self._new_notes
