"""Opt-in tests for a dedicated disposable PostgreSQL database only.

Never set these variables to a production target. Requires an explicit
loopback endpoint on a non-default port and a dedicated disposable database.
"""
import os
import re
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import Barrier

import psycopg
from psycopg import conninfo

from core.adapters.postgres_customer_repository import PostgresCustomerRepository
from core.domain.customer import Customer, CustomerId, CustomerName, CustomerAddress, CustomerCity


ROOT = Path(__file__).resolve().parents[3]
UP = ROOT / "migrations/postgres/0006_create_customers.up.sql"
DOWN = ROOT / "migrations/postgres/0006_create_customers.down.sql"
NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)


def disposable_parameters():
    if os.environ.get("AIOS_CUSTOMER_DISPOSABLE_TESTS") != "1":
        raise unittest.SkipTest("disposable PostgreSQL tests NOT_RUN: opt-in absent")
    url = os.environ.get("AIOS_CUSTOMER_TEST_DATABASE_URL")
    if not url:
        raise RuntimeError("explicit disposable database URL is required")
    try:
        values = conninfo.conninfo_to_dict(url)
        port = int(values.get("port", "5432"))
    except (ValueError, psycopg.Error) as exc:
        raise RuntimeError("invalid disposable target") from exc
    if (
        set(values) - {"host", "port", "dbname", "user", "password", "sslmode"}
        or values.get("host") != "127.0.0.1"
        or not 1024 <= port <= 65535 or port == 5432
        or not re.fullmatch(r"aios_customer_disposable_[a-z0-9_]+", values.get("dbname", ""))
        or values.get("user") != "postgres"
        or not values.get("password")
        or values.get("sslmode") not in (None, "disable")
    ):
        raise RuntimeError("target is not an admitted disposable PostgreSQL database")
    values["sslmode"] = "disable"
    values["connect_timeout"] = 5
    return values


class PostgresCustomerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parameters = disposable_parameters()

    def connect(self):
        return psycopg.connect(**self.parameters)

    def setUp(self):
        # Fail if a prior table exists: no destructive cleanup of unknown state.
        with self.connect() as connection:
            connection.execute(UP.read_text(encoding="utf-8"))

    def tearDown(self):
        with self.connect() as connection:
            connection.execute(DOWN.read_text(encoding="utf-8"))

    def repo(self, connection):
        return PostgresCustomerRepository(
            connection, event_id_source=lambda: "event",
            occurred_at_source=lambda: NOW,
        )

    def customer(self, identity="id", name="AB", notes=None):
        return Customer(
            CustomerId(identity), CustomerName(name), CustomerAddress("12345"),
            CustomerCity("CD"), notes,
            event_id_source=lambda: "event", occurred_at_source=lambda: NOW,
        )

    def test_round_trip_notes_and_event_lifecycle(self):
        with self.connect() as connection, connection.transaction():
            repo = self.repo(connection)
            for index, notes in enumerate((None, "", " ", "  line\n ", "quote ' %s")):
                customer = self.customer(str(index), notes=notes)
                before = customer.pending_events()
                self.assertIsNone(repo.save(customer))
                loaded = repo.get(customer.id)
                self.assertEqual(loaded.id, customer.id)
                self.assertEqual(loaded.name, customer.name)
                self.assertEqual(loaded.address, customer.address)
                self.assertEqual(loaded.city, customer.city)
                self.assertEqual(loaded.notes, notes)
                self.assertEqual(loaded.pending_events(), ())
                self.assertEqual(customer.pending_events(), before)

    def test_upsert_preserves_created_at_and_allows_duplicate_names(self):
        with self.connect() as connection, connection.transaction():
            repo = self.repo(connection)
            repo.save(self.customer())
            # Fixed historical value distinguishes preservation from a reset to
            # CURRENT_TIMESTAMP, even within this single transaction.
            connection.execute(
                "UPDATE customers SET created_at = %s WHERE customer_id = %s",
                (datetime(2000, 1, 1, tzinfo=timezone.utc), "id"),
            )
            repo.save(self.customer(name="Changed", notes="new"))
            repo.save(self.customer("other", name="Changed"))
            row = connection.execute(
                "SELECT name, notes, created_at FROM customers WHERE customer_id = %s",
                ("id",),
            ).fetchone()
            self.assertEqual(row, ("Changed", "new", datetime(2000, 1, 1, tzinfo=timezone.utc)))
            self.assertEqual(len(repo.list()), 2)

    def test_exists_delete_and_missing_get(self):
        with self.connect() as connection, connection.transaction():
            repo = self.repo(connection)
            identity = CustomerId("id")
            self.assertIsNone(repo.get(identity))
            self.assertFalse(repo.exists(identity))
            self.assertFalse(repo.delete(identity))
            repo.save(self.customer())
            self.assertTrue(repo.exists(identity))
            self.assertTrue(repo.delete(identity))
            self.assertFalse(repo.delete(identity))
            self.assertIsNone(repo.get(identity))

    def test_list_python_unicode_order(self):
        with self.connect() as connection, connection.transaction():
            repo = self.repo(connection)
            self.assertEqual(repo.list(), ())
            for identity in ("é", "a", "Z", "😀"):
                repo.save(self.customer(identity))
            self.assertEqual(tuple(c.id.value for c in repo.list()), ("Z", "a", "é", "😀"))

    def test_caller_rollback_restores_insert_update_and_delete(self):
        with self.connect() as connection, connection.transaction():
            self.repo(connection).save(self.customer())
        with self.connect() as connection:
            with self.assertRaises(RuntimeError):
                with connection.transaction():
                    repo = self.repo(connection)
                    repo.save(self.customer(name="Changed"))
                    repo.save(self.customer("new"))
                    repo.delete(CustomerId("id"))
                    raise RuntimeError("abort outer transaction")
        with self.connect() as connection, connection.transaction():
            repo = self.repo(connection)
            self.assertEqual(repo.get(CustomerId("id")).name.value, "AB")
            self.assertFalse(repo.exists(CustomerId("new")))

    def test_database_error_rolls_back_and_does_not_report_success(self):
        with self.connect() as connection:
            with self.assertRaises(psycopg.errors.CheckViolation):
                with connection.transaction():
                    connection.execute(
                        "ALTER TABLE customers ADD CONSTRAINT test_reject CHECK (name <> 'Rejected')"
                    )
                    repo = self.repo(connection)
                    repo.save(self.customer("first"))
                    repo.save(self.customer("second", name="Rejected"))
        with self.connect() as connection, connection.transaction():
            self.assertEqual(self.repo(connection).list(), ())

    def test_concurrent_upserts_create_one_identity(self):
        barrier = Barrier(2)

        def write(name):
            with self.connect() as connection, connection.transaction():
                connection.execute("SET LOCAL statement_timeout = '10s'")
                barrier.wait(timeout=10)
                self.repo(connection).save(self.customer(name=name))

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(write, name) for name in ("First", "Second")]
            for future in futures:
                future.result(timeout=20)
        with self.connect() as connection, connection.transaction():
            customers = self.repo(connection).list()
            self.assertEqual(len(customers), 1)
            self.assertIn(customers[0].name.value, ("First", "Second"))

    def test_migration_down_up_and_created_at_default(self):
        with self.connect() as connection, connection.transaction():
            connection.execute(DOWN.read_text(encoding="utf-8"))
            self.assertIsNone(connection.execute("SELECT to_regclass('customers')").fetchone()[0])
            connection.execute(UP.read_text(encoding="utf-8"))
            self.repo(connection).save(self.customer())
            created_at = connection.execute("SELECT created_at FROM customers").fetchone()[0]
            self.assertIsInstance(created_at, datetime)
            self.assertIsNotNone(created_at.tzinfo)


if __name__ == "__main__":
    unittest.main()
