"""Business authorization policy tests; no network or database."""
import copy
import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from core.app.customer_registration import Actor, CustomerRegistration

NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)
TEXT = 'catat_pelanggan {"name":"Ani","address":"Jalan 1","city":"Solo","notes":"  x  "}'

class MemoryTransactions:
    def __init__(self):
        self.owner = 42
        self.active = True
        self.last = 0
        self.rows = {}
        self.customers = {}
        self.audit_rows = []
        self.now = NOW
        self.fail_audit = False
        self.calls = 0

    @contextmanager
    def __call__(self):
        self.calls += 1
        before = copy.deepcopy(self.__dict__)
        try:
            yield self
        except Exception:
            self.__dict__.update(before)
            raise

    def lock_owner(self):
        return (self.owner, self.active, self.last)

    def advance_draft(self, message_id):
        self.last = message_id
        for row in self.rows.values():
            if row["state"] == "pending":
                row["state"] = "superseded"

    def by_request(self, message_id):
        return next((r.copy() for r in self.rows.values() if r["message_id"] == message_id), None)

    def by_token(self, token):
        row = self.rows.get(token)
        return None if row is None else row.copy()

    def clock(self):
        return self.now

    def add_confirmation(self, row):
        self.rows[row["token"]] = copy.deepcopy(row)

    def save_customer(self, customer):
        if customer.id.value in self.customers:
            raise RuntimeError("identity collision")
        self.customers[customer.id.value] = customer

    def audit(self, row, customer_id):
        if self.fail_audit:
            raise RuntimeError("audit unavailable")
        self.audit_rows.append((row["token"], customer_id))

    def consume(self, token, customer_id):
        self.rows[token].update(state="consumed", customer_id=customer_id)

class CustomerRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.tx = MemoryTransactions()
        self.app = CustomerRegistration(self.tx)
        self.actor = Actor(42, 42, "private", False)

    def send(self, message_id=1, text=TEXT, actor=None):
        return self.app.handle(actor or self.actor, message_id, text)

    def prepare(self):
        reply = self.send()
        token = next(iter(self.tx.rows))
        self.assertIn(token, reply)
        self.assertIn("600", reply)
        return token

    def confirm(self, token, message_id=2, actor=None):
        return self.send(message_id, "konfirmasi_pelanggan " + token, actor)

    def test_private_numeric_identity_only_and_deny_before_transaction(self):
        for actor in (Actor(True, 42, "private", False), Actor("42", 42, "private", False),
                      Actor(42, -5, "group", False), Actor(42, 43, "private", False),
                      Actor(42, 42, "private", True)):
            self.assertIn("ditolak", self.send(actor=actor))
        self.assertEqual(self.tx.calls, 0)

    def test_owner_must_be_enrolled_active_and_current(self):
        for identity, active in ((99, True), (42, False), (None, False)):
            self.tx.owner, self.tx.active = identity, active
            self.assertIn("ditolak", self.send())
        self.assertFalse(self.tx.rows)

    def test_prepare_only_preserves_snapshot_and_ten_minute_binding(self):
        token = self.prepare()
        row = self.tx.rows[token]
        self.assertEqual(row["expires_at"] - row["created_at"], timedelta(minutes=10))
        self.assertEqual((row["owner_id"], row["chat_id"]), (42, 42))
        self.assertEqual(row["snapshot"]["notes"], "  x  ")
        self.assertFalse(self.tx.customers)
        self.assertFalse(self.tx.audit_rows)

    def test_confirmation_atomic_save_audit_and_retry_receipt(self):
        token = self.prepare()
        first = self.confirm(token)
        self.assertIn("tersimpan", first)
        self.assertEqual(self.confirm(token, 3), first)
        self.assertEqual(len(self.tx.customers), 1)
        self.assertEqual(len(self.tx.audit_rows), 1)
        customer = next(iter(self.tx.customers.values()))
        self.assertEqual(len(customer.pending_events()), 1)
        self.assertEqual(self.tx.rows[token]["state"], "consumed")

    def test_audit_failure_rolls_back_save_and_consumption(self):
        token = self.prepare()
        self.tx.fail_audit = True
        with self.assertRaises(RuntimeError):
            self.confirm(token)
        self.assertFalse(self.tx.customers)
        self.assertEqual(self.tx.rows[token]["state"], "pending")

    def test_expiry_at_exact_boundary_and_after_is_denied(self):
        token = self.prepare()
        self.tx.now = NOW + timedelta(minutes=10)
        self.assertIn("kedaluwarsa", self.confirm(token))
        self.assertFalse(self.tx.customers)

    def test_new_valid_or_invalid_draft_invalidates_old_confirmation(self):
        for replacement in (TEXT.replace("Ani", "Budi"), 'catat_pelanggan {broken'):
            with self.subTest(replacement=replacement):
                self.setUp()
                token = self.prepare()
                self.send(2, replacement)
                self.assertIn("berlaku", self.confirm(token, 3))
                self.assertFalse(self.tx.customers)

    def test_duplicate_draft_and_out_of_order_retry_do_not_replace_newer(self):
        token = self.prepare()
        self.assertIn(token, self.send())
        self.send(3, TEXT.replace("Ani", "Budi"))
        self.assertIn("lama", self.send())
        self.assertEqual(len(self.tx.rows), 2)
        self.assertEqual(sum(r["state"] == "pending" for r in self.tx.rows.values()), 1)

    def test_confirmation_cannot_cross_identity_chat_or_message_order(self):
        token = self.prepare()
        self.assertIn("ditolak", self.confirm(token, actor=Actor(99, 99, "private", False)))
        self.assertIn("ditolak", self.confirm(token, 1))
        self.tx.rows[token]["chat_id"] = 43
        self.assertIn("ditolak", self.confirm(token))

    def test_revocation_blocks_pending_and_success_receipt(self):
        token = self.prepare()
        self.confirm(token)
        self.tx.active = False
        self.assertIn("ditolak", self.confirm(token, 3))

    def test_strict_json_fields_duplicate_keys_and_domain_validation(self):
        for payload in ('{}', '{"name":"Ani","name":"Budi"}', '[]',
                        '{"name":" Ani","address":"Jalan 1","city":"Solo"}',
                        '{"name":"Ani","address":"Jalan 1","city":"Solo","owner":42}',
                        '{"name":"Ani","address":"Jalan 1","city":"Solo","notes":false}'):
            self.assertIn("tidak valid", self.send(self.tx.last + 1, "catat_pelanggan " + payload))
        self.assertFalse(self.tx.rows)

    def test_unrelated_text_never_opens_transaction(self):
        self.assertIsNone(self.send(text="status"))
        self.assertEqual(self.tx.calls, 0)

    def test_telegram_edit_cancels_original_without_accepting_edited_payload(self):
        token = self.prepare()
        self.app.invalidate_edit(self.actor, 1)
        self.assertIn("berlaku", self.confirm(token))
        self.assertFalse(self.tx.customers)

    def test_expired_success_receipt_still_idempotent(self):
        token = self.prepare()
        first = self.confirm(token)
        self.tx.now += timedelta(days=1)
        self.assertEqual(self.confirm(token, 3), first)
        self.assertEqual(len(self.tx.customers), 1)

    def test_oversized_preview_is_rejected(self):
        import json
        payload = dict(name="Ani", address="Jalan 1", city="Solo", notes="x" * 3200)
        self.assertIn("tidak valid", self.send(text="catat_pelanggan " + json.dumps(payload)))
        self.assertFalse(self.tx.rows)

    def test_database_incompatible_unicode_and_deep_json_cancel_old_draft(self):
        import json
        for payload in (
            json.dumps(dict(name="Ani", address="Jalan 1", city="Solo", notes="\u0000")),
            json.dumps(dict(name="Ani", address="Jalan 1", city="Solo", notes="\ud800")),
            "[" * 1100 + "0" + "]" * 1100,
        ):
            with self.subTest(payload=payload[:80]):
                self.setUp()
                token = self.prepare()
                self.assertIn("tidak valid", self.send(2, "catat_pelanggan " + payload))
                self.assertIn("berlaku", self.confirm(token, 3))
                self.assertFalse(self.tx.customers)

    def test_token_syntax_and_message_id_fail_closed(self):
        for value in (True, 0, -1, "1"):
            self.assertIn("ditolak", self.send(value))
        self.assertIn("tidak valid", self.send(text="konfirmasi_pelanggan guessed"))

if __name__ == "__main__":
    unittest.main()
