"""Customer aggregate root."""

from collections.abc import Callable
from datetime import datetime

from core.domain.aggregate_root import AggregateRoot
from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName
from core.domain.customer.event_factory import CustomerEventFactory
from core.domain.exceptions import DomainValidationError


class Customer(AggregateRoot[CustomerId]):
    """Customer aggregate with pending domain-event recording."""

    __slots__ = (
        "_name",
        "_address",
        "_city",
        "_notes",
        "_event_factory",
        "_event_id_source",
        "_occurred_at_source",
    )

    def __init__(
        self,
        customer_id: CustomerId,
        name: CustomerName,
        address: CustomerAddress,
        city: CustomerCity,
        notes: str | None = None,
        *,
        event_id_source: Callable[[], object],
        occurred_at_source: Callable[[], datetime],
    ) -> None:
        if type(customer_id) is not CustomerId:
            raise DomainValidationError("id must be a CustomerId")
        self._require_exact(name, CustomerName, "name")
        self._require_exact(address, CustomerAddress, "address")
        self._require_exact(city, CustomerCity, "city")
        self._require_notes(notes)
        self._require_callable(event_id_source, "event_id_source")
        self._require_callable(occurred_at_source, "occurred_at_source")
        super().__init__(customer_id)
        self._event_factory = CustomerEventFactory()
        self._event_id_source = event_id_source
        self._occurred_at_source = occurred_at_source
        event_id, occurred_at = self._event_metadata()
        event = self._event_factory.create_customer_created(
            id=event_id,
            occurred_at=occurred_at,
            customer_id=customer_id,
            name=name,
            address=address,
            city=city,
            notes=notes,
        )
        self._name = name
        self._address = address
        self._city = city
        self._notes = notes
        self.record_event(event)

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

    def change_name(self, name: CustomerName) -> None:
        self._require_exact(name, CustomerName, "name")
        if name == self._name:
            return
        previous_name = self._name
        event_id, occurred_at = self._event_metadata()
        event = self._event_factory.create_customer_name_changed(
            id=event_id,
            occurred_at=occurred_at,
            customer_id=self.id,
            previous_name=previous_name,
            new_name=name,
        )
        self._name = name
        self.record_event(event)

    def change_address(self, address: CustomerAddress) -> None:
        self._require_exact(address, CustomerAddress, "address")
        if address == self._address:
            return
        previous_address = self._address
        event_id, occurred_at = self._event_metadata()
        event = self._event_factory.create_customer_address_changed(
            id=event_id,
            occurred_at=occurred_at,
            customer_id=self.id,
            previous_address=previous_address,
            new_address=address,
        )
        self._address = address
        self.record_event(event)

    def change_city(self, city: CustomerCity) -> None:
        self._require_exact(city, CustomerCity, "city")
        if city == self._city:
            return
        previous_city = self._city
        event_id, occurred_at = self._event_metadata()
        event = self._event_factory.create_customer_city_changed(
            id=event_id,
            occurred_at=occurred_at,
            customer_id=self.id,
            previous_city=previous_city,
            new_city=city,
        )
        self._city = city
        self.record_event(event)

    def change_notes(self, notes: str | None) -> None:
        self._require_notes(notes)
        if notes == self._notes:
            return
        previous_notes = self._notes
        event_id, occurred_at = self._event_metadata()
        event = self._event_factory.create_customer_notes_changed(
            id=event_id,
            occurred_at=occurred_at,
            customer_id=self.id,
            previous_notes=previous_notes,
            new_notes=notes,
        )
        self._notes = notes
        self.record_event(event)

    def _event_metadata(self) -> tuple[object, datetime]:
        return self._event_id_source(), self._occurred_at_source()

    @staticmethod
    def _require_exact(value: object, expected: type, field: str) -> None:
        if type(value) is not expected:
            raise DomainValidationError(f"{field} must be a {expected.__name__}")

    @staticmethod
    def _require_notes(notes: str | None) -> None:
        if notes is not None and not isinstance(notes, str):
            raise DomainValidationError("notes must be a str or None")

    @staticmethod
    def _require_callable(value: object, field: str) -> None:
        if not callable(value):
            raise DomainValidationError(f"{field} must be callable")
