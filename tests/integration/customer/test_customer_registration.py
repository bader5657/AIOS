"""Run only in the existing admitted disposable Customer PostgreSQL database."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Barrier
import unittest
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg import conninfo, sql

from test_postgres_customer_repository import disposable_parameters
from core.app.customer_registration import Actor, CustomerRegistration
from core.adapters.postgres_customer_registration import PostgresCustomerRegistrationTransactions, _Transaction
from scripts.bootstrap_business_owner import enroll

ROOT = Path(__file__).resolve().parents[3]
TEXT = 'catat_pelanggan {"name":"Ani","address":"Jalan 1","city":"Solo","notes":"  x  "}'
ACTOR = Actor(42, 42, "private", False)

class CustomerRegistrationIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parameters = disposable_parameters()

    def admin(self):
        return psycopg.connect(**self.parameters)

    def setUp(self):
        self.role = "aios_customer_test_" + uuid4().hex
        password = uuid4().hex
        with self.admin() as connection:
            # No IF NOT EXISTS / destructive pre-clean: unknown state must fail.
            for filename in ("0006_create_customers.up.sql", "0007_customer_registration.up.sql"):
                connection.execute((ROOT / "migrations/postgres" / filename).read_text())
            connection.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEROLE NOINHERIT").format(sql.Identifier(self.role), sql.Literal(password)))
            for grant in (
                "GRANT USAGE ON SCHEMA public TO {}",
                "GRANT SELECT, INSERT, UPDATE ON customers TO {}",
                "GRANT SELECT, UPDATE(last_draft_message_id) ON business_owner TO {}",
                "GRANT SELECT, INSERT, UPDATE ON customer_confirmations TO {}",
                "GRANT SELECT, INSERT ON customer_registration_audit TO {}",
            ):
                connection.execute(sql.SQL(grant).format(sql.Identifier(self.role)))
            enroll(connection, 42, "disposable:synthetic-verified-identity", "disposable:test-approval")
        values = dict(self.parameters, user=self.role, password=password)
        self.dsn = conninfo.make_conninfo(**values)
        self.app = CustomerRegistration(PostgresCustomerRegistrationTransactions(self.dsn))

    def tearDown(self):
        with self.admin() as connection:
            for filename in ("0007_customer_registration.down.sql", "0006_create_customers.down.sql"):
                connection.execute((ROOT / "migrations/postgres" / filename).read_text())
            connection.execute(sql.SQL("REVOKE USAGE ON SCHEMA public FROM {}").format(sql.Identifier(self.role)))
            connection.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(self.role)))

    def send(self, mid=1, text=TEXT, actor=ACTOR):
        return self.app.handle(actor, mid, text)

    def prepare(self):
        self.send()
        with self.admin() as connection:
            return connection.execute("SELECT token FROM customer_confirmations").fetchone()[0]

    def confirm(self, token, mid=2):
        return self.send(mid, "konfirmasi_pelanggan " + token)

    def counts(self):
        with self.admin() as connection:
            return tuple(connection.execute("SELECT count(*) FROM " + table).fetchone()[0]
                         for table in ("customers", "customer_registration_audit"))

    def test_roundtrip_commit_receipt_and_restart_retry(self):
        token = self.prepare()
        reply = self.confirm(token)
        self.app = CustomerRegistration(PostgresCustomerRegistrationTransactions(self.dsn))
        self.assertEqual(self.confirm(token, 3), reply)
        self.assertEqual(self.counts(), (1,1))
        with self.admin() as connection:
            self.assertEqual(connection.execute("SELECT notes FROM customers").fetchone()[0], "  x  ")
            self.assertEqual(connection.execute("SELECT state FROM customer_confirmations").fetchone()[0], "consumed")

    def test_concurrent_confirmation_exactly_once(self):
        token = self.prepare()
        barrier = Barrier(2)
        def run(mid):
            barrier.wait(timeout=10)
            return self.confirm(token, mid)
        with ThreadPoolExecutor(max_workers=2) as executor:
            replies = list(executor.map(run, (2,3)))
        self.assertEqual(replies[0], replies[1])
        self.assertEqual(self.counts(), (1,1))

    def test_concurrent_duplicate_draft_returns_same_confirmation(self):
        barrier = Barrier(2)
        def run(_):
            barrier.wait(timeout=10)
            return self.send()
        with ThreadPoolExecutor(max_workers=2) as executor:
            replies = list(executor.map(run, (1,2)))
        self.assertEqual(replies[0], replies[1])
        with self.admin() as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM customer_confirmations").fetchone()[0], 1)

    def test_audit_failure_rolls_back_customer_and_consumption(self):
        token = self.prepare()
        with patch.object(_Transaction, "audit", side_effect=RuntimeError("injected")):
            with self.assertRaises(RuntimeError):
                self.confirm(token)
        self.assertEqual(self.counts(), (0,0))
        self.assertIn("tersimpan", self.confirm(token, 3))

    def test_expiry_during_persistence_rolls_back_everything(self):
        token = self.prepare()
        original = _Transaction.save_customer
        # Use a single timestamp to preserve the exact ten-minute DB constraint.
        def expire(tx, customer):
            original(tx, customer)
            tx.connection.execute("UPDATE customer_confirmations SET created_at = t.now - INTERVAL '11 minutes', expires_at = t.now - INTERVAL '1 minute' FROM (SELECT clock_timestamp() AS now) t")
        with patch.object(_Transaction, "save_customer", expire):
            with self.assertRaises(RuntimeError):
                self.confirm(token)
        self.assertEqual(self.counts(), (0,0))

    def test_expired_or_superseded_confirmation_cannot_save(self):
        token = self.prepare()
        with self.admin() as connection:
            connection.execute("UPDATE customer_confirmations SET created_at = created_at - INTERVAL '11 minutes', expires_at = expires_at - INTERVAL '11 minutes'")
        self.assertIn("kedaluwarsa", self.confirm(token))
        self.send(3, TEXT.replace("Ani", "Budi"))
        self.assertIn("berlaku", self.confirm(token, 4))
        self.assertEqual(self.counts(), (0,0))

    def test_revocation_and_wrong_identity_deny(self):
        self.assertIn("ditolak", self.send(actor=Actor(99,99,"private",False)))
        token = self.prepare()
        with self.admin() as connection:
            connection.execute("UPDATE business_owner SET active = FALSE")
        self.assertIn("ditolak", self.confirm(token))
        self.assertEqual(self.counts(), (0,0))

    def test_runtime_cannot_enroll_or_change_authority_or_mutate_audit(self):
        for statement in (
            "INSERT INTO business_owner(telegram_user_id, verification_evidence, approval_reference) VALUES (99,'x','x')",
            "UPDATE business_owner SET active = FALSE",
            "UPDATE business_owner SET telegram_user_id = 99",
            "DELETE FROM customer_registration_audit",
            "TRUNCATE customer_registration_audit",
        ):
            with self.subTest(statement=statement), self.assertRaises(psycopg.errors.InsufficientPrivilege):
                with psycopg.connect(self.dsn) as connection:
                    connection.execute(statement)

    def test_superuser_runtime_is_rejected_and_bootstrap_cannot_replace_owner(self):
        unsafe = CustomerRegistration(PostgresCustomerRegistrationTransactions(conninfo.make_conninfo(**self.parameters)))
        with self.assertRaises(PermissionError):
            unsafe.handle(ACTOR,1,TEXT)
        with self.assertRaises(psycopg.errors.UniqueViolation):
            with self.admin() as connection:
                enroll(connection, 99, "test:identity", "test:approval")

    def test_audit_is_append_only_even_for_schema_owner(self):
        token = self.prepare()
        self.confirm(token)
        for statement in ("UPDATE customer_registration_audit SET action='catat_pelanggan'",
                          "DELETE FROM customer_registration_audit", "TRUNCATE customer_registration_audit"):
            with self.subTest(statement=statement), self.assertRaises(psycopg.Error):
                with self.admin() as connection:
                    connection.execute(statement)
        self.assertEqual(self.counts(), (1,1))

    def test_postgresql_invalid_unicode_replacement_commits_invalidation(self):
        import json
        token = self.prepare()
        payload = json.dumps(dict(name="Ani", address="Jalan 1", city="Solo", notes="\u0000"))
        self.assertIn("tidak valid", self.send(2, "catat_pelanggan " + payload))
        self.assertIn("berlaku", self.confirm(token, 3))
        self.assertEqual(self.counts(), (0,0))

    def test_existing_customer_identity_is_never_overwritten(self):
        token = self.prepare()
        with self.admin() as connection:
            connection.execute("INSERT INTO customers(customer_id,name,address,city) VALUES (%s,'Original','Jalan 1','Solo')", ("tg-customer-"+token,))
        with self.assertRaises(RuntimeError):
            self.confirm(token)
        with self.admin() as connection:
            self.assertEqual(connection.execute("SELECT name FROM customers").fetchone()[0], "Original")
        self.assertEqual(self.counts(), (1,0))
