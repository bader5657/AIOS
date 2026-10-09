"""Isolated CustomerDraft contract tests."""
import unittest

from core.app.customer_draft import CustomerDraft
from core.domain.customer.customer_name import CustomerName
from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.exceptions import DomainValidationError


class CustomerDraftTests(unittest.TestCase):
    def test_partial_draft_and_missing_order(self):
        draft = CustomerDraft(city="Solo")
        self.assertEqual(draft.missing_fields(), ("name", "address"))
        self.assertFalse(draft.is_complete)
        with self.assertRaises(DomainValidationError):
            draft.snapshot()
        draft.set_name("AB")
        draft.set_address("12345")
        self.assertTrue(draft.is_complete)
        self.assertEqual(draft.snapshot()["city"], "Solo")

    def test_empty_draft_cannot_be_snapshotted(self):
        draft = CustomerDraft()
        self.assertEqual(draft.missing_fields(), ("name", "address", "city"))
        with self.assertRaises(DomainValidationError):
            draft.snapshot()

    def test_required_inputs_match_domain(self):
        fields = (("name", CustomerName, "AB"), ("address", CustomerAddress, "12345"),
                  ("city", CustomerCity, "CD"))
        for field, validator, minimum in fields:
            values = ("", " ", minimum[:-1], " " + minimum, minimum + " ",
                      42, False, [], {}, minimum, minimum + "  X", minimum + "\nX")
            for value in values:
                with self.subTest(field=field, value=value):
                    try:
                        expected = validator(value).value
                    except DomainValidationError:
                        with self.assertRaises(DomainValidationError):
                            CustomerDraft(**{field: value})
                        draft = CustomerDraft(**{field: minimum})
                        with self.assertRaises(DomainValidationError):
                            getattr(draft, "set_" + field)(value)
                        self.assertEqual(getattr(draft, field), minimum)
                    else:
                        draft = CustomerDraft(**{field: value})
                        self.assertEqual(getattr(draft, field), expected)
                        getattr(draft, "set_" + field)(value)
                        self.assertEqual(getattr(draft, field), expected)

    def test_none_setter_rejected_without_losing_value(self):
        draft = CustomerDraft(name="AB", address="12345", city="CD")
        for field in ("name", "address", "city"):
            with self.subTest(field=field):
                previous = getattr(draft, field)
                with self.assertRaises(DomainValidationError):
                    getattr(draft, "set_" + field)(None)
                self.assertEqual(getattr(draft, field), previous)

    def test_notes_preserved_including_none_empty_and_whitespace(self):
        for notes in (None, "", " ", "  line one\nline  two  "):
            with self.subTest(notes=notes):
                draft = CustomerDraft(name="AB", address="12345", city="CD", notes=notes)
                self.assertEqual(draft.snapshot()["notes"], notes)
                draft.set_notes(notes)
                self.assertEqual(draft.snapshot()["notes"], notes)

    def test_invalid_notes_are_rejected_atomically(self):
        for notes in (42, False, [], {}):
            with self.subTest(notes=notes):
                with self.assertRaises(DomainValidationError):
                    CustomerDraft(notes=notes)
                draft = CustomerDraft(notes="original")
                with self.assertRaises(DomainValidationError):
                    draft.set_notes(notes)
                self.assertEqual(draft.notes, "original")

    def test_snapshot_revalidates_direct_assignment(self):
        for field, value in (("name", "A"), ("address", "1234"),
                             ("city", " C"), ("notes", 42)):
            with self.subTest(field=field):
                draft = CustomerDraft(name="AB", address="12345", city="CD")
                setattr(draft, field, value)
                self.assertFalse(draft.is_complete)
                with self.assertRaises(DomainValidationError):
                    draft.snapshot()

    def test_snapshot_is_detached_and_preserves_values(self):
        draft = CustomerDraft(name="AB  CD", address="12345\n678", city="CD")
        snapshot = draft.snapshot()
        self.assertEqual(snapshot, {"name": "AB  CD", "address": "12345\n678",
                                    "city": "CD", "notes": None})
        draft.set_name("EF")
        self.assertEqual(snapshot["name"], "AB  CD")
        snapshot["city"] = "XX"
        self.assertEqual(draft.city, "CD")


if __name__ == "__main__":
    unittest.main()
