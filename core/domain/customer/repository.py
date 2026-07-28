"""Abstract Customer repository contract."""

from core.domain.customer.customer import Customer
from core.domain.customer.customer_id import CustomerId
from core.domain.repository import Repository


class CustomerRepository(Repository[Customer, CustomerId]):
    """Abstract repository interface for Customer aggregates.

    The five operations are inherited without redeclaration. ``save`` creates
    or updates the single logical entry identified by ``Customer.id`` and
    returns ``None``; saving an existing ``CustomerId`` replaces that entry
    without duplication or a duplicate error. No Customer-field uniqueness is
    imposed.

    ``get`` returns the matching Customer or ``None`` when missing. ``exists``
    returns whether a matching entry exists without side effects. ``delete``
    returns ``True`` when it removes an entry and ``False`` for a missing entry,
    for which deletion is a no-op.

    ``list`` returns every entry exactly once as an immutable tuple ordered by
    ``Customer.id.value`` in ascending Python string order, or the empty tuple
    when no entries exist.

    This interface defines no storage state or concrete implementation. It
    performs no persistence, infrastructure, serialization, transaction,
    event inspection, recording, publication, dispatch, or envelope behavior,
    and exposes no query, search, filtering, pagination, or counting API.
    """

    __slots__ = ()
