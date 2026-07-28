"""Stateless factory for published Customer domain events."""

from __future__ import annotations

from datetime import datetime

from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName
from core.domain.customer.events import (
    CustomerAddressChanged,
    CustomerCityChanged,
    CustomerCreated,
    CustomerNameChanged,
    CustomerNotesChanged,
)


class CustomerEventFactory:
    """Create Customer event records from caller-supplied values."""

    __slots__ = ()

    def create_customer_created(
        self,
        *,
        id: object,
        occurred_at: datetime,
        customer_id: CustomerId,
        name: CustomerName,
        address: CustomerAddress,
        city: CustomerCity,
        notes: str | None,
    ) -> CustomerCreated:
        return CustomerCreated(
            id=id,
            occurred_at=occurred_at,
            event_name="customer.created",
            customer_id=customer_id,
            name=name,
            address=address,
            city=city,
            notes=notes,
        )

    def create_customer_name_changed(
        self,
        *,
        id: object,
        occurred_at: datetime,
        customer_id: CustomerId,
        previous_name: CustomerName,
        new_name: CustomerName,
    ) -> CustomerNameChanged:
        return CustomerNameChanged(
            id=id,
            occurred_at=occurred_at,
            event_name="customer.name_changed",
            customer_id=customer_id,
            previous_name=previous_name,
            new_name=new_name,
        )

    def create_customer_address_changed(
        self,
        *,
        id: object,
        occurred_at: datetime,
        customer_id: CustomerId,
        previous_address: CustomerAddress,
        new_address: CustomerAddress,
    ) -> CustomerAddressChanged:
        return CustomerAddressChanged(
            id=id,
            occurred_at=occurred_at,
            event_name="customer.address_changed",
            customer_id=customer_id,
            previous_address=previous_address,
            new_address=new_address,
        )

    def create_customer_city_changed(
        self,
        *,
        id: object,
        occurred_at: datetime,
        customer_id: CustomerId,
        previous_city: CustomerCity,
        new_city: CustomerCity,
    ) -> CustomerCityChanged:
        return CustomerCityChanged(
            id=id,
            occurred_at=occurred_at,
            event_name="customer.city_changed",
            customer_id=customer_id,
            previous_city=previous_city,
            new_city=new_city,
        )

    def create_customer_notes_changed(
        self,
        *,
        id: object,
        occurred_at: datetime,
        customer_id: CustomerId,
        previous_notes: str | None,
        new_notes: str | None,
    ) -> CustomerNotesChanged:
        return CustomerNotesChanged(
            id=id,
            occurred_at=occurred_at,
            event_name="customer.notes_changed",
            customer_id=customer_id,
            previous_notes=previous_notes,
            new_notes=new_notes,
        )
