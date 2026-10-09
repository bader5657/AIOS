"""Synchronous Customer persistence within a caller-owned transaction."""

from collections.abc import Callable
from datetime import datetime

from psycopg import Connection
from psycopg.pq import TransactionStatus
from psycopg.rows import tuple_row

from core.domain.customer import Customer, CustomerAddress, CustomerCity, CustomerId, CustomerName
from core.domain.customer.repository import CustomerRepository
from core.domain.exceptions import DomainValidationError


_COLUMNS = "customer_id, name, address, city, notes"


class PostgresCustomerRepository(CustomerRepository):
    """Use an active non-autocommit transaction supplied by the caller.

    The caller owns connection lifetime, commit and rollback. A successful
    method is not a durability receipt: the outer transaction must commit.
    Database errors propagate. Pending events are neither drained nor stored.
    """

    def __init__(
        self,
        connection: Connection,
        *,
        event_id_source: Callable[[], object],
        occurred_at_source: Callable[[], datetime],
    ) -> None:
        if not callable(event_id_source) or not callable(occurred_at_source):
            raise DomainValidationError("event metadata sources must be callable")
        self._connection = connection
        self._event_id_source = event_id_source
        self._occurred_at_source = occurred_at_source

    def _require_transaction(self) -> None:
        if (
            self._connection.autocommit
            or self._connection.info.transaction_status != TransactionStatus.INTRANS
        ):
            raise RuntimeError("an active caller-owned non-autocommit transaction is required")

    @staticmethod
    def _identity(customer_id: CustomerId) -> str:
        if type(customer_id) is not CustomerId:
            raise DomainValidationError("id must be a CustomerId")
        return customer_id.value

    def _customer(self, row: tuple) -> Customer:
        return Customer.reconstitute(
            CustomerId(row[0]), CustomerName(row[1]), CustomerAddress(row[2]),
            CustomerCity(row[3]), row[4],
            event_id_source=self._event_id_source,
            occurred_at_source=self._occurred_at_source,
        )

    def save(self, aggregate: Customer) -> None:
        if type(aggregate) is not Customer:
            raise DomainValidationError("aggregate must be a Customer")
        identity = self._identity(aggregate.id)
        self._require_transaction()
        with self._connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                """INSERT INTO customers (customer_id, name, address, city, notes)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (customer_id) DO UPDATE SET
                       name = EXCLUDED.name, address = EXCLUDED.address,
                       city = EXCLUDED.city, notes = EXCLUDED.notes""",
                (identity, aggregate.name.value, aggregate.address.value,
                 aggregate.city.value, aggregate.notes),
            )

    def get(self, entity_id: CustomerId) -> Customer | None:
        identity = self._identity(entity_id)
        self._require_transaction()
        with self._connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                f"SELECT {_COLUMNS} FROM customers WHERE customer_id = %s", (identity,)
            )
            row = cursor.fetchone()
        return None if row is None else self._customer(row)

    def exists(self, entity_id: CustomerId) -> bool:
        identity = self._identity(entity_id)
        self._require_transaction()
        with self._connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM customers WHERE customer_id = %s)",
                (identity,),
            )
            return cursor.fetchone()[0]

    def delete(self, entity_id: CustomerId) -> bool:
        identity = self._identity(entity_id)
        self._require_transaction()
        with self._connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                "DELETE FROM customers WHERE customer_id = %s RETURNING customer_id",
                (identity,),
            )
            return cursor.fetchone() is not None

    def list(self) -> tuple[Customer, ...]:
        self._require_transaction()
        with self._connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(f"SELECT {_COLUMNS} FROM customers")
            rows = cursor.fetchall()
        customers = (self._customer(row) for row in rows)
        return tuple(sorted(customers, key=lambda customer: customer.id.value))
