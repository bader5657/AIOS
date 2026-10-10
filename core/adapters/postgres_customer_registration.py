"""PostgreSQL unit of work for the single-owner customer capability."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from core.adapters.postgres_customer_repository import PostgresCustomerRepository

class PostgresCustomerRegistrationTransactions:
    """Fresh connection, committed before any successful Telegram reply.

    Runtime must be a non-superuser, non-schema-owner role without enrollment
    or audit mutation privileges. Bootstrap uses a separate administrative role.
    """
    def __init__(self, dsn):
        if not dsn:
            raise ValueError("explicit business database DSN is required")
        self._dsn = dsn

    @contextmanager
    def __call__(self):
        with psycopg.connect(self._dsn, autocommit=False) as connection:
            with connection.transaction():
                connection.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                row = connection.execute("""
                    SELECT r.rolsuper OR r.rolcreaterole OR r.rolbypassrls
                      OR has_table_privilege(current_user, 'business_owner', 'INSERT,DELETE,TRUNCATE')
                      OR has_column_privilege(current_user, 'business_owner', 'active', 'UPDATE')
                      OR has_column_privilege(current_user, 'business_owner', 'telegram_user_id', 'UPDATE')
                      OR has_table_privilege(current_user, 'customer_registration_audit', 'UPDATE,DELETE,TRUNCATE')
                      OR pg_has_role(current_user, c.relowner, 'MEMBER')
                    FROM pg_roles r, pg_class c
                    WHERE r.rolname = current_user AND c.oid = 'business_owner'::regclass
                """).fetchone()
                if row is None or row[0]:
                    raise PermissionError("business runtime database role is overprivileged")
                yield _Transaction(connection)

class _Transaction:
    def __init__(self, connection):
        self.connection = connection

    def lock_owner(self):
        return self.connection.execute(
            "SELECT telegram_user_id, active, last_draft_message_id "
            "FROM business_owner WHERE singleton = TRUE FOR UPDATE"
        ).fetchone()

    def advance_draft(self, message_id):
        self.connection.execute(
            "UPDATE business_owner SET last_draft_message_id = %s WHERE singleton = TRUE",
            (message_id,),
        )
        self.connection.execute(
            "UPDATE customer_confirmations SET state = 'superseded' WHERE state = 'pending'"
        )

    def _one(self, sql, parameters):
        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, parameters)
            return cursor.fetchone()

    def by_request(self, message_id):
        return self._one("SELECT * FROM customer_confirmations WHERE message_id = %s", (message_id,))

    def by_token(self, token):
        return self._one("SELECT * FROM customer_confirmations WHERE token = %s FOR UPDATE", (token,))

    def clock(self):
        # PostgreSQL CURRENT_TIMESTAMP is transaction-start time; do not use it
        # for TTL after waiting for another transaction's lock.
        return self.connection.execute("SELECT clock_timestamp()").fetchone()[0]

    def add_confirmation(self, row):
        self.connection.execute(
            """INSERT INTO customer_confirmations
               (token, owner_id, chat_id, message_id, snapshot, created_at, expires_at, state)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'pending')""",
            (row["token"], row["owner_id"], row["chat_id"], row["message_id"],
             Jsonb(row["snapshot"]), row["created_at"], row["expires_at"]),
        )

    def save_customer(self, customer):
        # The published repository uses upsert. Lock against competing DML and
        # check absence so this create-only capability can never overwrite.
        self.connection.execute("LOCK TABLE customers IN SHARE ROW EXCLUSIVE MODE")
        repo = PostgresCustomerRepository(
            self.connection, event_id_source=lambda: str(uuid4()),
            occurred_at_source=lambda: datetime.now(timezone.utc),
        )
        if repo.exists(customer.id):
            raise RuntimeError("customer identity collision")
        repo.save(customer)

    def audit(self, row, customer_id):
        digest = hashlib.sha256(
            json.dumps(row["snapshot"], ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.connection.execute(
            """INSERT INTO customer_registration_audit
               (confirmation_token, owner_id, chat_id, customer_id, snapshot_sha256)
               VALUES (%s,%s,%s,%s,%s)""",
            (row["token"], row["owner_id"], row["chat_id"], customer_id, digest),
        )

    def consume(self, token, customer_id):
        result = self.connection.execute(
            """UPDATE customer_confirmations SET state = 'consumed', customer_id = %s
               WHERE token = %s AND state = 'pending' AND expires_at > clock_timestamp()""",
            (customer_id, token),
        )
        if result.rowcount != 1:
            # Also rolls back Customer and audit if expiry occurred while waiting
            # for a customer table lock or during persistence.
            raise RuntimeError("confirmation expired during persistence")
