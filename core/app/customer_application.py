"""Convert validated customer input into an unsaved domain aggregate."""

from collections.abc import Callable
from datetime import datetime

from core.app.customer_draft import CustomerDraft
from core.domain.customer.customer import Customer
from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName


class CustomerApplication:
    """Construct customers without persistence or event publication."""

    __slots__ = ()

    def create_customer_from_draft(
        self,
        draft: CustomerDraft,
        customer_id: CustomerId,
        *,
        event_id_source: Callable[[], object],
        occurred_at_source: Callable[[], datetime],
    ) -> Customer:
        """Use one validated snapshot; Customer records its creation event.

        Identity and metadata sources are supplied by the caller. Domain
        validation and source failures propagate unchanged. The returned
        aggregate is unsaved and retains its pending CustomerCreated event.
        """
        snapshot = draft.snapshot()
        return Customer(
            customer_id=customer_id,
            name=CustomerName(snapshot["name"]),
            address=CustomerAddress(snapshot["address"]),
            city=CustomerCity(snapshot["city"]),
            notes=snapshot["notes"],
            event_id_source=event_id_source,
            occurred_at_source=occurred_at_source,
        )
