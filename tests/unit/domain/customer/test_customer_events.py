"""Tests for the published DF-04.4 Customer domain-event records."""

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
import unittest

import core.domain.customer.events as events_module
from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName
from core.domain.customer.events import (
    CustomerAddressChanged,
    CustomerCityChanged,
    CustomerCreated,
    CustomerNameChanged,
    CustomerNotesChanged,
)
from core.domain.domain_event import DomainEvent
from core.domain.exceptions import DomainValidationError


EVENT_CLASSES = (
    CustomerCreated,
    CustomerNameChanged,
    CustomerAddressChanged,
    CustomerCityChanged,
    CustomerNotesChanged,
)

EVENT_NAMES = {
    CustomerCreated: "customer.created",
    CustomerNameChanged: "customer.name_changed",
    CustomerAddressChanged: "customer.address_changed",
    CustomerCityChanged: "customer.city_changed",
    CustomerNotesChanged: "customer.notes_changed",
}

PAYLOAD_FIELDS = {
    CustomerCreated: ("customer_id", "name", "address", "city", "notes"),
    CustomerNameChanged: ("customer_id", "previous_name", "new_name"),
    CustomerAddressChanged: (
        "customer_id",
        "previous_address",
        "new_address",
    ),
    CustomerCityChanged: ("customer_id", "previous_city", "new_city"),
    CustomerNotesChanged: ("customer_id", "previous_notes", "new_notes"),
}


class CustomerEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.occurred_at = datetime(2026, 7, 29, 9, 0, tzinfo=timezone.utc)
        self.customer_id = CustomerId("customer-001")
        self.name = CustomerName("Customer One")
        self.new_name = CustomerName("Customer Two")
        self.address = CustomerAddress("First Address")
        self.new_address = CustomerAddress("Second Address")
        self.city = CustomerCity("Jakarta")
        self.new_city = CustomerCity("Surabaya")

    def kwargs_for(self, event_class: type[DomainEvent]) -> dict[str, object]:
        common = {
            "id": "event-001",
            "occurred_at": self.occurred_at,
            "event_name": EVENT_NAMES[event_class],
            "customer_id": self.customer_id,
        }
        payloads = {
            CustomerCreated: {
                "name": self.name,
                "address": self.address,
                "city": self.city,
                "notes": "  notes verbatim  ",
            },
            CustomerNameChanged: {
                "previous_name": self.name,
                "new_name": self.new_name,
            },
            CustomerAddressChanged: {
                "previous_address": self.address,
                "new_address": self.new_address,
            },
            CustomerCityChanged: {
                "previous_city": self.city,
                "new_city": self.new_city,
            },
            CustomerNotesChanged: {
                "previous_notes": None,
                "new_notes": "  notes verbatim  ",
            },
        }
        return common | payloads[event_class]

    def make(self, event_class: type[DomainEvent], **changes: object) -> DomainEvent:
        values = self.kwargs_for(event_class) | changes
        return event_class(**values)

    def test_exactly_five_concrete_customer_event_classes_are_published(self) -> None:
        self.assertEqual(
            events_module.__all__,
            (
                "CustomerCreated",
                "CustomerNameChanged",
                "CustomerAddressChanged",
                "CustomerCityChanged",
                "CustomerNotesChanged",
            ),
        )
        concrete_events = {
            value
            for value in vars(events_module).values()
            if inspect.isclass(value)
            and value.__module__ == events_module.__name__
            and issubclass(value, DomainEvent)
            and not inspect.isabstract(value)
        }
        self.assertEqual(concrete_events, set(EVENT_CLASSES))

    def test_all_events_inherit_domain_event(self) -> None:
        for event_class in EVENT_CLASSES:
            with self.subTest(event_class=event_class.__name__):
                self.assertTrue(issubclass(event_class, DomainEvent))

    def test_constructor_signatures_are_exact_and_keyword_only(self) -> None:
        expected_payloads = PAYLOAD_FIELDS
        for event_class in EVENT_CLASSES:
            with self.subTest(event_class=event_class.__name__):
                parameters = inspect.signature(event_class).parameters
                self.assertEqual(
                    tuple(parameters),
                    ("id", "occurred_at", "event_name")
                    + expected_payloads[event_class],
                )
                self.assertTrue(
                    all(
                        parameter.kind is inspect.Parameter.KEYWORD_ONLY
                        for parameter in parameters.values()
                    )
                )
                with self.assertRaises(TypeError):
                    event_class(*self.kwargs_for(event_class).values())

    def test_exact_event_names_and_valid_construction(self) -> None:
        for event_class in EVENT_CLASSES:
            with self.subTest(event_class=event_class.__name__):
                event = self.make(event_class)
                values = self.kwargs_for(event_class)
                self.assertIsInstance(event, DomainEvent)
                self.assertEqual(event.event_name, EVENT_NAMES[event_class])
                self.assertEqual(event.id, values["id"])
                self.assertIs(event.occurred_at, self.occurred_at)
                for field in PAYLOAD_FIELDS[event_class]:
                    self.assertIs(getattr(event, field), values[field])

    def test_mismatched_event_names_are_rejected_without_normalization(self) -> None:
        for event_class in EVENT_CLASSES:
            for event_name in (
                "wrong.event",
                f" {EVENT_NAMES[event_class]} ",
                EVENT_NAMES[event_class].upper(),
            ):
                with self.subTest(
                    event_class=event_class.__name__,
                    event_name=event_name,
                ):
                    with self.assertRaises(DomainValidationError):
                        self.make(event_class, event_name=event_name)

    def test_inherited_base_validation_is_preserved(self) -> None:
        for event_class in EVENT_CLASSES:
            invalid_fields = (
                ("id", None),
                ("occurred_at", None),
                ("occurred_at", "2026-07-29"),
                ("occurred_at", datetime(2026, 7, 29, 9, 0)),
                ("event_name", None),
            )
            for field, value in invalid_fields:
                with self.subTest(
                    event_class=event_class.__name__,
                    field=field,
                    value=value,
                ):
                    with self.assertRaises(DomainValidationError):
                        self.make(event_class, **{field: value})

    def test_customer_created_requires_exact_payload_types(self) -> None:
        invalid = {
            "customer_id": (None, "customer-001"),
            "name": (None, "Customer One"),
            "address": (None, "First Address"),
            "city": (None, "Jakarta"),
            "notes": (0, False, object()),
        }
        for field, values in invalid.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(DomainValidationError):
                        self.make(CustomerCreated, **{field: value})

    def test_changed_events_require_exact_customer_value_object_types(self) -> None:
        cases = (
            (CustomerNameChanged, "previous_name", (None, "Customer One")),
            (CustomerNameChanged, "new_name", (None, "Customer Two")),
            (
                CustomerAddressChanged,
                "previous_address",
                (None, "First Address"),
            ),
            (CustomerAddressChanged, "new_address", (None, "Second Address")),
            (CustomerCityChanged, "previous_city", (None, "Jakarta")),
            (CustomerCityChanged, "new_city", (None, "Surabaya")),
        )
        for event_class, field, values in cases:
            for value in values:
                with self.subTest(event_class=event_class.__name__, field=field):
                    with self.assertRaises(DomainValidationError):
                        self.make(event_class, **{field: value})

    def test_every_event_requires_exact_customer_id_type(self) -> None:
        for event_class in EVENT_CLASSES:
            for value in (None, "customer-001", object()):
                with self.subTest(event_class=event_class.__name__, value=value):
                    with self.assertRaises(DomainValidationError):
                        self.make(event_class, customer_id=value)

    def test_changed_previous_and_new_values_must_differ(self) -> None:
        equal_values = (
            (CustomerNameChanged, "new_name", CustomerName("Customer One")),
            (
                CustomerAddressChanged,
                "new_address",
                CustomerAddress("First Address"),
            ),
            (CustomerCityChanged, "new_city", CustomerCity("Jakarta")),
            (CustomerNotesChanged, "new_notes", None),
        )
        for event_class, field, value in equal_values:
            with self.subTest(event_class=event_class.__name__):
                with self.assertRaises(DomainValidationError):
                    self.make(event_class, **{field: value})

    def test_notes_accept_str_or_none_and_preserve_values_verbatim(self) -> None:
        created_values = (None, "", " ", "  created notes  ")
        for notes in created_values:
            with self.subTest(event_class="CustomerCreated", notes=notes):
                self.assertIs(self.make(CustomerCreated, notes=notes).notes, notes)

        changed_values = (
            (None, ""),
            ("", None),
            (" before ", " after "),
        )
        for previous, new in changed_values:
            with self.subTest(previous=previous, new=new):
                event = self.make(
                    CustomerNotesChanged,
                    previous_notes=previous,
                    new_notes=new,
                )
                self.assertIs(event.previous_notes, previous)
                self.assertIs(event.new_notes, new)

    def test_notes_reject_values_other_than_exact_str_or_none(self) -> None:
        for event_class, fields in (
            (CustomerCreated, ("notes",)),
            (CustomerNotesChanged, ("previous_notes", "new_notes")),
        ):
            for field in fields:
                for value in (0, False, [], object()):
                    with self.subTest(
                        event_class=event_class.__name__,
                        field=field,
                        value=value,
                    ):
                        with self.assertRaises(DomainValidationError):
                            self.make(event_class, **{field: value})

    def test_all_base_and_payload_fields_are_immutable(self) -> None:
        replacements = {
            "id": "event-002",
            "occurred_at": self.occurred_at + timedelta(seconds=1),
            "event_name": "customer.invalid",
            "customer_id": CustomerId("customer-002"),
            "name": self.new_name,
            "address": self.new_address,
            "city": self.new_city,
            "notes": "different",
            "previous_name": self.new_name,
            "new_name": self.name,
            "previous_address": self.new_address,
            "new_address": self.address,
            "previous_city": self.new_city,
            "new_city": self.city,
            "previous_notes": "before",
            "new_notes": "after",
        }
        for event_class in EVENT_CLASSES:
            event = self.make(event_class)
            fields = ("id", "occurred_at", "event_name") + PAYLOAD_FIELDS[event_class]
            for field in fields:
                for attribute in (field, f"_{field}"):
                    with self.subTest(
                        event_class=event_class.__name__,
                        attribute=attribute,
                    ):
                        with self.assertRaises(AttributeError):
                            setattr(event, attribute, replacements[field])

    def test_equal_events_have_equal_hashes_and_work_in_collections(self) -> None:
        for event_class in EVENT_CLASSES:
            with self.subTest(event_class=event_class.__name__):
                first = self.make(event_class)
                second = self.make(event_class)
                self.assertEqual(first, second)
                self.assertEqual(hash(first), hash(second))
                self.assertEqual({first: "value"}[second], "value")
                self.assertIn(second, {first})

    def test_any_differing_base_field_makes_events_unequal(self) -> None:
        for event_class in EVENT_CLASSES:
            event = self.make(event_class)
            differences = (
                {"id": "event-002"},
                {"occurred_at": self.occurred_at + timedelta(seconds=1)},
            )
            for difference in differences:
                with self.subTest(
                    event_class=event_class.__name__,
                    difference=difference,
                ):
                    self.assertNotEqual(event, self.make(event_class, **difference))

    def test_any_differing_payload_field_makes_events_unequal(self) -> None:
        differences = {
            CustomerCreated: (
                {"customer_id": CustomerId("customer-002")},
                {"name": self.new_name},
                {"address": self.new_address},
                {"city": self.new_city},
                {"notes": "different"},
            ),
            CustomerNameChanged: (
                {"customer_id": CustomerId("customer-002")},
                {"previous_name": CustomerName("Customer Zero")},
                {"new_name": CustomerName("Customer Three")},
            ),
            CustomerAddressChanged: (
                {"customer_id": CustomerId("customer-002")},
                {"previous_address": CustomerAddress("Earlier Address")},
                {"new_address": CustomerAddress("Third Address")},
            ),
            CustomerCityChanged: (
                {"customer_id": CustomerId("customer-002")},
                {"previous_city": CustomerCity("Bandung")},
                {"new_city": CustomerCity("Semarang")},
            ),
            CustomerNotesChanged: (
                {"customer_id": CustomerId("customer-002")},
                {"previous_notes": "before"},
                {"new_notes": "after"},
            ),
        }
        for event_class, changes in differences.items():
            event = self.make(event_class)
            for change in changes:
                with self.subTest(
                    event_class=event_class.__name__,
                    change=change,
                ):
                    self.assertNotEqual(event, self.make(event_class, **change))

    def test_different_concrete_event_classes_and_non_events_are_unequal(self) -> None:
        events = [self.make(event_class) for event_class in EVENT_CLASSES]
        for index, event in enumerate(events):
            for other in events[index + 1 :]:
                self.assertNotEqual(event, other)
            self.assertNotEqual(event, object())

    def test_no_generation_or_integration_api_is_published(self) -> None:
        prohibited = {
            "create",
            "factory",
            "generate",
            "record_event",
            "dispatch",
            "publish",
            "persist",
            "serialize",
            "envelope",
            "save",
        }
        for event_class in EVENT_CLASSES:
            public_api = {
                name for name in vars(event_class) if not name.startswith("_")
            }
            self.assertEqual(
                public_api,
                set(PAYLOAD_FIELDS[event_class]),
            )
            self.assertTrue(prohibited.isdisjoint(public_api))

    def test_only_standard_library_and_published_domain_dependencies_imported(
        self,
    ) -> None:
        path = (
            Path(__file__).parents[4]
            / "core"
            / "domain"
            / "customer"
            / "events.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "__future__",
                "datetime",
                "core.domain.customer.customer_address",
                "core.domain.customer.customer_city",
                "core.domain.customer.customer_id",
                "core.domain.customer.customer_name",
                "core.domain.domain_event",
                "core.domain.exceptions",
            },
        )
        source_names = {
            node.id.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        } | {
            node.attr.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
        }
        prohibited_names = {
            "uuid",
            "now",
            "utcnow",
            "record_event",
            "eventfactory",
            "dispatcher",
            "eventbus",
            "publisher",
            "repository",
            "eventenvelope",
            "json",
            "database",
            "infrastructure",
        }
        self.assertTrue(prohibited_names.isdisjoint(source_names))


if __name__ == "__main__":
    unittest.main()
