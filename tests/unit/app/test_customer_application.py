"""Acceptance tests for isolated draft-to-Customer conversion."""

import unittest
from datetime import datetime, timezone

from core.app.customer_application import CustomerApplication
from core.app.customer_draft import CustomerDraft
from core.domain.customer.customer import Customer
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.events import CustomerCreated
from core.domain.exceptions import DomainValidationError


NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)


class CustomerApplicationTests(unittest.TestCase):
    def setUp(self):
        self.app = CustomerApplication()
        self.customer_id = CustomerId("customer-1")
        self.calls = []

    def event_id(self):
        self.calls.append("id")
        return "event-1"

    def occurred_at(self):
        self.calls.append("time")
        return NOW

    def draft(self, notes=None):
        return CustomerDraft("AB  CD", "12345\n678", "Solo", notes)

    def create(self, draft, **overrides):
        arguments = {
            "customer_id": self.customer_id,
            "event_id_source": self.event_id,
            "occurred_at_source": self.occurred_at,
        }
        arguments.update(overrides)
        return self.app.create_customer_from_draft(draft, **arguments)

    def test_returns_customer_with_one_complete_domain_event(self):
        customer = self.create(self.draft("note"))
        self.assertIs(type(customer), Customer)
        self.assertIs(customer.id, self.customer_id)
        self.assertEqual(customer.name.value, "AB  CD")
        self.assertEqual(customer.address.value, "12345\n678")
        self.assertEqual(customer.city.value, "Solo")
        self.assertEqual(customer.notes, "note")
        events = customer.pending_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertIs(type(event), CustomerCreated)
        self.assertEqual(event.id, "event-1")
        self.assertEqual(event.occurred_at, NOW)
        self.assertEqual(event.event_name, "customer.created")
        self.assertEqual(event.customer_id, self.customer_id)
        self.assertEqual(event.name.value, "AB  CD")
        self.assertEqual(event.address.value, "12345\n678")
        self.assertEqual(event.city.value, "Solo")
        self.assertEqual(event.notes, "note")
        self.assertEqual(self.calls, ["id", "time"])

    def test_uses_one_snapshot_without_rereading_mutated_draft(self):
        class ChangingDraft(CustomerDraft):
            def snapshot(self):
                self.snapshot_calls += 1
                result = super().snapshot()
                self.set_name("Later")
                self.set_address("Later address")
                self.set_city("Later city")
                self.set_notes("later notes")
                return result

        draft = ChangingDraft("Original", "Original address", "Solo", "original notes")
        draft.snapshot_calls = 0
        customer = self.create(draft)
        self.assertEqual(draft.snapshot_calls, 1)
        self.assertEqual(customer.name.value, "Original")
        self.assertEqual(customer.address.value, "Original address")
        self.assertEqual(customer.city.value, "Solo")
        self.assertEqual(customer.notes, "original notes")

    def test_draft_is_unchanged_and_later_edits_do_not_change_customer(self):
        draft = self.draft("original")
        customer = self.create(draft)
        self.assertEqual(
            (draft.name, draft.address, draft.city, draft.notes),
            ("AB  CD", "12345\n678", "Solo", "original"),
        )
        draft.set_name("Later")
        draft.set_address("Later address")
        draft.set_city("Later city")
        draft.set_notes("later")
        self.assertEqual(customer.name.value, "AB  CD")
        self.assertEqual(customer.address.value, "12345\n678")
        self.assertEqual(customer.city.value, "Solo")
        self.assertEqual(customer.notes, "original")
        self.assertEqual(customer.pending_events()[0].notes, "original")

    def test_notes_are_preserved_verbatim(self):
        for notes in (None, "", " ", "  line one\nline  two  "):
            with self.subTest(notes=notes):
                customer = self.create(self.draft(notes))
                self.assertEqual(customer.notes, notes)
                self.assertEqual(customer.pending_events()[0].notes, notes)

    def test_incomplete_draft_fails_before_metadata_is_consumed(self):
        for field in ("name", "address", "city"):
            with self.subTest(field=field):
                draft = self.draft()
                setattr(draft, field, None)
                with self.assertRaises(DomainValidationError):
                    self.create(draft)
        self.assertEqual(self.calls, [])

    def test_invalid_direct_assignment_is_revalidated_without_normalizing(self):
        for field, value in (
            ("name", " AB"), ("name", "A"), ("address", "1234"),
            ("city", "Solo "), ("city", 42), ("notes", []),
        ):
            with self.subTest(field=field, value=value):
                draft = self.draft()
                setattr(draft, field, value)
                with self.assertRaises(DomainValidationError):
                    self.create(draft)
                self.assertEqual(getattr(draft, field), value)
        self.assertEqual(self.calls, [])

    def test_customer_id_must_be_the_domain_value_object(self):
        for value in ("customer-1", None, 42):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    self.create(self.draft(), customer_id=value)
        self.assertEqual(self.calls, [])

    def test_both_metadata_sources_are_required(self):
        for supplied in (
            {}, {"event_id_source": self.event_id},
            {"occurred_at_source": self.occurred_at},
        ):
            with self.subTest(supplied=supplied):
                with self.assertRaises(TypeError):
                    self.app.create_customer_from_draft(
                        self.draft(), self.customer_id, **supplied
                    )
        self.assertEqual(self.calls, [])

    def test_non_callable_metadata_sources_are_rejected(self):
        for field in ("event_id_source", "occurred_at_source"):
            with self.subTest(field=field):
                with self.assertRaises(DomainValidationError):
                    self.create(self.draft(), **{field: None})
        self.assertEqual(self.calls, [])

    def test_invalid_metadata_results_are_rejected_by_domain(self):
        for overrides in (
            {"event_id_source": lambda: None},
            {"occurred_at_source": lambda: datetime(2026, 10, 10)},
            {"occurred_at_source": lambda: "2026-10-10"},
        ):
            with self.subTest(overrides=overrides):
                draft = self.draft("keep")
                with self.assertRaises(DomainValidationError):
                    self.create(draft, **overrides)
                self.assertEqual(draft.notes, "keep")
                self.assertEqual(draft.name, "AB  CD")

    def test_metadata_source_failure_propagates_without_changing_draft(self):
        error = RuntimeError("source unavailable")

        def fail():
            raise error

        for field in ("event_id_source", "occurred_at_source"):
            with self.subTest(field=field):
                draft = self.draft("keep")
                with self.assertRaises(RuntimeError) as caught:
                    self.create(draft, **{field: fail})
                self.assertIs(caught.exception, error)
                self.assertEqual(
                    (draft.name, draft.address, draft.city, draft.notes),
                    ("AB  CD", "12345\n678", "Solo", "keep"),
                )

    def test_repeated_creation_has_independent_pending_events(self):
        draft = self.draft()
        first = self.create(draft)
        second = self.create(draft)
        self.assertIsNot(first, second)
        self.assertEqual(len(first.pull_events()), 1)
        self.assertEqual(first.pending_events(), ())
        self.assertEqual(len(second.pending_events()), 1)
        self.assertEqual(self.calls, ["id", "time", "id", "time"])


if __name__ == "__main__":
    unittest.main()
