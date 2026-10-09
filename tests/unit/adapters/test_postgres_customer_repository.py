"""Isolated adapter contract tests; no PostgreSQL connection."""
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

import psycopg
from psycopg.pq import TransactionStatus
from psycopg.rows import tuple_row

from core.adapters.postgres_customer_repository import PostgresCustomerRepository
from core.domain.customer import Customer, CustomerId, CustomerName, CustomerAddress, CustomerCity
from core.domain.exceptions import DomainValidationError


NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)


class Cursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, parameters=None):
        self.connection.statements.append((sql, parameters))
        if self.connection.error is not None:
            raise self.connection.error

    def fetchone(self):
        return self.connection.row

    def fetchall(self):
        return self.connection.rows


class Connection:
    def __init__(self):
        self.autocommit = False
        self.info = SimpleNamespace(transaction_status=TransactionStatus.INTRANS)
        self.row = None
        self.rows = []
        self.error = None
        self.statements = []

    def cursor(self, *, row_factory):
        if row_factory is not tuple_row:
            raise AssertionError("tuple rows required independent of connection defaults")
        return Cursor(self)

    def commit(self):
        raise AssertionError("adapter must not commit")

    def rollback(self):
        raise AssertionError("adapter must not rollback")

    def close(self):
        raise AssertionError("adapter must not close caller connection")


class PostgresCustomerRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.connection = Connection()
        self.calls = []
        self.repo = PostgresCustomerRepository(
            self.connection, event_id_source=self.event_id,
            occurred_at_source=self.occurred_at,
        )

    def event_id(self):
        self.calls.append("id")
        return "event"

    def occurred_at(self):
        self.calls.append("time")
        return NOW

    def customer(self):
        return Customer(
            CustomerId("id-1"), CustomerName("AB"), CustomerAddress("12345"),
            CustomerCity("CD"), "  notes\n ",
            event_id_source=self.event_id, occurred_at_source=self.occurred_at,
        )

    def test_save_parameterizes_values_and_preserves_pending_events(self):
        customer = self.customer()
        before = customer.pending_events()
        self.assertIsNone(self.repo.save(customer))
        sql, values = self.connection.statements[0]
        self.assertIn("ON CONFLICT (customer_id) DO UPDATE", sql)
        self.assertNotIn("created_at =", sql)
        self.assertEqual(values, ("id-1", "AB", "12345", "CD", "  notes\n "))
        self.assertEqual(customer.pending_events(), before)
        self.assertEqual(self.calls, ["id", "time"])

    def test_get_reconstitutes_without_events_and_retains_mutation_sources(self):
        self.connection.row = ("id-1", "AB", "12345", "CD", None)
        customer = self.repo.get(CustomerId("id-1"))
        self.assertEqual(customer.id, CustomerId("id-1"))
        self.assertEqual(customer.name.value, "AB")
        self.assertEqual(customer.address.value, "12345")
        self.assertEqual(customer.city.value, "CD")
        self.assertIsNone(customer.notes)
        self.assertEqual(customer.pending_events(), ())
        self.assertEqual(self.calls, [])
        customer.change_notes("changed")
        self.assertEqual(len(customer.pending_events()), 1)
        self.assertEqual(self.calls, ["id", "time"])

    def test_missing_get_and_exists_delete_boolean_results(self):
        self.assertIsNone(self.repo.get(CustomerId("missing")))
        for value in (False, True):
            self.connection.row = (value,)
            self.assertIs(self.repo.exists(CustomerId("id")), value)
        self.connection.row = None
        self.assertIs(self.repo.delete(CustomerId("id")), False)
        self.connection.row = ("id",)
        self.assertIs(self.repo.delete(CustomerId("id")), True)

    def test_list_uses_python_order_and_returns_tuple(self):
        self.connection.rows = [
            (identity, "AB", "12345", "CD", "")
            for identity in ("é", "a", "Z", "😀")
        ]
        customers = self.repo.list()
        self.assertIs(type(customers), tuple)
        self.assertEqual(tuple(c.id.value for c in customers), ("Z", "a", "é", "😀"))
        self.assertTrue(all(c.pending_events() == () for c in customers))
        self.assertEqual(self.calls, [])
        self.connection.rows = []
        self.assertEqual(self.repo.list(), ())

    def test_notes_are_preserved_and_corrupt_rows_are_rejected(self):
        for notes in (None, "", " ", "  line\n "):
            self.connection.row = ("id", "AB", "12345", "CD", notes)
            self.assertEqual(self.repo.get(CustomerId("id")).notes, notes)
        for row in (
            (" id", "AB", "12345", "CD", None),
            ("id", " A", "12345", "CD", None),
            ("id", "AB", "1234", "CD", None),
            ("id", "AB", "12345", "C", None),
            ("id", "AB", "12345", "CD", 1),
        ):
            self.connection.row = row
            with self.assertRaises(DomainValidationError):
                self.repo.get(CustomerId("id"))
        self.assertEqual(self.calls, [])

    def test_invalid_arguments_and_sources_are_rejected(self):
        for method in (self.repo.get, self.repo.exists, self.repo.delete):
            with self.assertRaises(DomainValidationError):
                method("id")
        with self.assertRaises(DomainValidationError):
            self.repo.save(object())
        for sources in ((None, self.occurred_at), (self.event_id, None)):
            with self.assertRaises(DomainValidationError):
                PostgresCustomerRepository(
                    self.connection, event_id_source=sources[0],
                    occurred_at_source=sources[1],
                )
        self.assertEqual(self.connection.statements, [])

    def test_all_operations_require_active_non_autocommit_transaction(self):
        customer = self.customer()
        operations = (
            lambda: self.repo.save(customer), lambda: self.repo.get(customer.id),
            lambda: self.repo.exists(customer.id), lambda: self.repo.delete(customer.id),
            self.repo.list,
        )
        for autocommit, status in (
            (True, TransactionStatus.INTRANS), (False, TransactionStatus.IDLE),
            (False, TransactionStatus.INERROR), (False, TransactionStatus.UNKNOWN),
        ):
            self.connection.autocommit = autocommit
            self.connection.info.transaction_status = status
            for operation in operations:
                with self.assertRaises(RuntimeError):
                    operation()
        self.assertEqual(self.connection.statements, [])

    def test_database_failure_propagates_without_consuming_events(self):
        customer = self.customer()
        before = customer.pending_events()
        error = psycopg.OperationalError("test failure")
        self.connection.error = error
        for operation in (
            lambda: self.repo.save(customer), lambda: self.repo.get(customer.id),
            lambda: self.repo.exists(customer.id), lambda: self.repo.delete(customer.id),
            self.repo.list,
        ):
            with self.assertRaises(psycopg.OperationalError) as caught:
                operation()
            self.assertIs(caught.exception, error)
        self.assertEqual(customer.pending_events(), before)


if __name__ == "__main__":
    unittest.main()
