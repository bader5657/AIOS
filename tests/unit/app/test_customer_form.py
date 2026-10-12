"""Form v1 behavior through the existing application transaction contract."""
import unittest
from datetime import timedelta
from core.app.customer_registration import Actor, CustomerRegistration
from core.app.customer_draft import CustomerDraft
from core.domain.exceptions import DomainValidationError
from test_customer_registration import MemoryTransactions

FORM = "Nama: Ani Fiktif\nAlamat: Jalan Uji 123\nKota: Solo\nNo. Telp: +62 0812-0000\nKet: Catatan uji"

class CustomerFormTests(unittest.TestCase):
    def setUp(self):
        self.tx = MemoryTransactions()
        self.app = CustomerRegistration(self.tx)
        self.actor = Actor(42, 42, "private", False)

    def send(self, text, mid=1, actor=None):
        return self.app.handle(actor or self.actor, mid, text)

    def draft(self, text=FORM, mid=2):
        reply = self.send(text, mid)
        self.assertIsInstance(reply, str)
        self.assertIn("konfirmasi_pelanggan", reply)
        return next(r["token"] for r in self.tx.rows.values() if r["message_id"] == mid)

    def confirm(self, token, mid=3):
        return self.send("konfirmasi_pelanggan " + token, mid)

    def test_start_is_owner_authorized_and_returns_five_field_template(self):
        reply = self.send("catat pelanggan")
        self.assertIsInstance(reply, str)
        for label in ("Nama:", "Alamat:", "Kota:", "No. Telp:", "Ket:"):
            self.assertIn(label, reply)
        self.assertFalse(self.tx.customers)
        self.assertFalse(self.tx.rows)

    def test_start_form_and_cancel_deny_nonowner_or_revoked_owner(self):
        for command in ("catat pelanggan", FORM, "batal pelanggan"):
            self.assertEqual(self.send(command, actor=Actor(99,99,"private",False)), "Akses ditolak.")
            self.tx.active = False
            self.assertEqual(self.send(command), "Akses ditolak.")
            self.tx.active = True
        self.assertFalse(self.tx.rows)

    def test_phone_roundtrip_creation_event_audit_and_retry(self):
        token = self.draft()
        self.assertFalse(self.tx.customers)
        self.assertEqual(self.tx.rows[token]["snapshot"]["phone"], "+62 0812-0000")
        first = self.confirm(token)
        self.assertIn("tersimpan", first)
        self.assertEqual(self.confirm(token, 4), first)
        customer = next(iter(self.tx.customers.values()))
        self.assertEqual(customer.phone, "+62 0812-0000")
        self.assertEqual(customer.pending_events()[0].phone, "+62 0812-0000")
        self.assertEqual(len(self.tx.customers), 1)
        self.assertEqual(len(self.tx.audit_rows), 1)

    def test_blank_optional_fields_and_layout_whitespace(self):
        token = self.draft("Nama:  Ani  \nAlamat: Jalan Uji 123\nKota: Solo\nNo. Telp:\nKet:")
        self.assertEqual(self.tx.rows[token]["snapshot"], dict(name="Ani",address="Jalan Uji 123",city="Solo",notes=None))
        self.confirm(token)
        self.assertIsNone(next(iter(self.tx.customers.values())).phone)

    def test_optional_labels_can_be_omitted_and_header_copied(self):
        token = self.draft("Masukkan data pelanggan:\nNama: Ani\nAlamat: Jalan Uji 123\nKota: Solo")
        self.assertIsNone(self.tx.rows[token]["snapshot"]["notes"])

    def test_invalid_replacement_cancels_pending_without_save(self):
        for suffix in ("\nNama: Other", "\nUnknown: value", "\ntext without colon"):
            self.setUp()
            token = self.draft()
            reply = self.send(FORM + suffix, 3)
            self.assertIn("tidak valid", reply)
            self.assertIn("berlaku", self.confirm(token, 4))
            self.assertFalse(self.tx.customers)

    def test_required_fields_remain_subject_to_domain_contract(self):
        for form in (FORM.replace("Nama: Ani Fiktif","Nama:"),
                     FORM.replace("Alamat: Jalan Uji 123","Alamat: x"),
                     FORM.replace("Kota: Solo","Kota:"),
                     FORM.replace("Nama: Ani Fiktif","Nama: A")):
            self.assertIn("tidak valid", self.send(form, self.tx.last+1))
        self.assertFalse(self.tx.rows)

    def test_phone_invalid_format_type_and_controls_rejected(self):
        for phone in ("not-a-phone", "12+34", "0"*65):
            self.assertIn("tidak valid", self.send(FORM.replace("+62 0812-0000", phone), self.tx.last+1))
        import inspect
        self.assertIn("phone", inspect.signature(CustomerDraft).parameters)
        for phone in (123, True, "012\n34", "\x00"):
            with self.assertRaises(DomainValidationError):
                CustomerDraft("Ani", "Jalan Uji 123", "Solo", phone=phone)

    def test_cancel_consumes_no_customer_and_repeated_cancel_is_safe(self):
        token = self.draft()
        self.assertIn("dibatalkan", self.send("batal pelanggan", 3))
        self.assertIn("dibatalkan", self.send("batal pelanggan", 3))
        self.assertIn("berlaku", self.confirm(token, 4))
        self.assertFalse(self.tx.customers)
        newer = self.draft(mid=5)
        self.send("batal pelanggan", 3)
        self.assertIn("tersimpan", self.confirm(newer, 6))

    def test_start_cancels_pending_but_old_start_cannot_cancel_newer(self):
        token = self.draft()
        self.send("catat pelanggan", 3)
        self.assertIn("berlaku", self.confirm(token, 4))
        newer = self.draft(mid=5)
        self.send("catat pelanggan", 3)
        self.assertIn("tersimpan", self.confirm(newer, 6))

    def test_duplicate_form_retains_token_and_expiry(self):
        token = self.draft()
        expiry = self.tx.rows[token]["expires_at"]
        self.tx.now += timedelta(minutes=1)
        self.assertIn(token, self.send(FORM, 2))
        self.assertEqual(self.tx.rows[token]["expires_at"], expiry)
        self.assertEqual(len(self.tx.rows), 1)

    def test_form_edit_invalidates_same_confirmation(self):
        token = self.draft()
        self.app.invalidate_edit(self.actor, 2)
        self.assertIn("berlaku", self.confirm(token))
        self.assertFalse(self.tx.customers)

    def test_json_phone_extension_preserves_zero_prefix(self):
        text = 'catat_pelanggan {"name":"Ani","address":"Jalan Uji 123","city":"Solo","phone":"001234","notes":null}'
        token = self.draft(text=text)
        self.confirm(token)
        self.assertEqual(next(iter(self.tx.customers.values())).phone, "001234")

    def test_form_audit_failure_rolls_back_phone_customer_and_consumption(self):
        token = self.draft()
        self.tx.fail_audit = True
        with self.assertRaises(RuntimeError):
            self.confirm(token)
        self.assertFalse(self.tx.customers)
        self.assertEqual(self.tx.rows[token]["state"], "pending")

    def test_group_bot_or_mismatched_private_chat_is_denied(self):
        for actor in (Actor(42,-1,"group",False),Actor(42,42,"private",True),Actor(42,43,"private",False)):
            self.assertEqual(self.send(FORM, actor=actor), "Akses ditolak.")
        self.assertFalse(self.tx.rows)
