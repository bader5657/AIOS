"""Customer aggregate root."""

from core.domain.aggregate_root import AggregateRoot
from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName
from core.domain.exceptions import DomainValidationError


class Customer(AggregateRoot[CustomerId]):
    """Customer aggregate without event-creation integration."""

    __slots__ = ("_name", "_address", "_city", "_notes")

    def __init__(self, customer_id: CustomerId, name: CustomerName, address: CustomerAddress, city: CustomerCity, notes: str | None = None) -> None:
        if type(customer_id) is not CustomerId:
            raise DomainValidationError("id must be a CustomerId")
        self._require_exact(name, CustomerName, "name")
        self._require_exact(address, CustomerAddress, "address")
        self._require_exact(city, CustomerCity, "city")
        self._require_notes(notes)
        super().__init__(customer_id)
        self._name = name
        self._address = address
        self._city = city
        self._notes = notes

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
        if name != self._name:
            self._name = name

    def change_address(self, address: CustomerAddress) -> None:
        self._require_exact(address, CustomerAddress, "address")
        if address != self._address:
            self._address = address

    def change_city(self, city: CustomerCity) -> None:
        self._require_exact(city, CustomerCity, "city")
        if city != self._city:
            self._city = city

    def change_notes(self, notes: str | None) -> None:
        self._require_notes(notes)
        if notes != self._notes:
            self._notes = notes

    @staticmethod
    def _require_exact(value: object, expected: type, field: str) -> None:
        if type(value) is not expected:
            raise DomainValidationError(f"{field} must be a {expected.__name__}")

    @staticmethod
    def _require_notes(notes: str | None) -> None:
        if notes is not None and not isinstance(notes, str):
            raise DomainValidationError("notes must be a str or None")
