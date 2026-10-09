"""Partial customer input; no persistence or runtime integration."""

from dataclasses import dataclass

from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_name import CustomerName
from core.domain.exceptions import DomainValidationError


@dataclass(slots=True)
class CustomerDraft:
    """None marks an uncollected required field; values are never normalized.

    Setters validate before assignment. Snapshot validation also protects
    against invalid values assigned directly to the draft's public fields.
    A snapshot contains input values only, not a Customer or a save receipt.
    """

    name: str | None = None
    address: str | None = None
    city: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        self._validate_supplied()

    def set_name(self, value: str) -> None:
        self.name = CustomerName(value).value

    def set_address(self, value: str) -> None:
        self.address = CustomerAddress(value).value

    def set_city(self, value: str) -> None:
        self.city = CustomerCity(value).value

    def set_notes(self, value: str | None) -> None:
        self._validate_notes(value)
        self.notes = value

    def missing_fields(self) -> tuple[str, ...]:
        return tuple(
            field for field in ("name", "address", "city")
            if getattr(self, field) is None
        )

    @property
    def is_complete(self) -> bool:
        try:
            self.validate()
        except DomainValidationError:
            return False
        return True

    def validate(self) -> None:
        """Require every mandatory field and validate all supplied values."""
        self._validate_supplied()
        missing = self.missing_fields()
        if missing:
            raise DomainValidationError(
                "Missing customer fields: " + ", ".join(missing)
            )

    def snapshot(self) -> dict[str, str | None]:
        """Return a fresh complete snapshot without changing the draft."""
        self.validate()
        return {
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "notes": self.notes,
        }

    def _validate_supplied(self) -> None:
        if self.name is not None:
            CustomerName(self.name)
        if self.address is not None:
            CustomerAddress(self.address)
        if self.city is not None:
            CustomerCity(self.city)
        self._validate_notes(self.notes)

    @staticmethod
    def _validate_notes(value: str | None) -> None:
        # Customer's published notes contract permits str or None verbatim.
        if value is not None and not isinstance(value, str):
            raise DomainValidationError("notes must be a str or None")
