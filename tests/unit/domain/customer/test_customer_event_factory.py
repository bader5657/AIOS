"""Tests for the published DF-04.5 Customer event factory."""

from __future__ import annotations

import ast
from datetime import datetime, timezone
import inspect
from pathlib import Path
import unittest

import core.domain.customer.event_factory as factory_module
from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.customer_name import CustomerName
from core.domain.customer.event_factory import CustomerEventFactory
from core.domain.customer.events import (
    CustomerAddressChanged,
    CustomerCityChanged,
    CustomerCreated,
    CustomerNameChanged,
    CustomerNotesChanged,
)
from core.domain.exceptions import DomainValidationError


METHOD_CASES = {
    "create_customer_created": (
        CustomerCreated,
        ("id", "occurred_at", "customer_id", "name", "address", "city", "notes"),
        "customer.created",
    ),
    "create_customer_name_changed": (
        CustomerNameChanged,
        ("id", "occurred_at", "customer_id", "previous_name", "new_name"),
        "customer.name_changed",
    ),
    "create_customer_address_changed": (
        CustomerAddressChanged,
        (
            "id",
            "occurred_at",
            "customer_id",
            "previous_address",
            "new_address",
        ),
        "customer.address_changed",
    ),
    "create_customer_city_changed": (
        CustomerCityChanged,
        ("id", "occurred_at", "customer_id", "previous_city", "new_city"),
        "customer.city_changed",
    ),
    "create_customer_notes_changed": (
        CustomerNotesChanged,
        ("id", "occurred_at", "customer_id", "previous_notes", "new_notes"),
        "customer.notes_changed",
    ),
}


class CustomerEventFactoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = CustomerEventFactory()
        self.occurred_at = datetime(2026, 7, 29, 9, 0, tzinfo=timezone.utc)
        self.customer_id = CustomerId("customer-001")
        self.name = CustomerName("Customer One")
        self.new_name = CustomerName("Customer Two")
        self.address = CustomerAddress("First Address")
        self.new_address = CustomerAddress("Second Address")
        self.city = CustomerCity("Jakarta")
        self.new_city = CustomerCity("Surabaya")

    def kwargs_for(self, method_name: str) -> dict[str, object]:
        payloads = {
            "create_customer_created": {
                "name": self.name,
                "address": self.address,
                "city": self.city,
                "notes": "  notes verbatim  ",
            },
            "create_customer_name_changed": {
                "previous_name": self.name,
                "new_name": self.new_name,
            },
            "create_customer_address_changed": {
                "previous_address": self.address,
                "new_address": self.new_address,
            },
            "create_customer_city_changed": {
                "previous_city": self.city,
                "new_city": self.new_city,
            },
            "create_customer_notes_changed": {
                "previous_notes": None,
                "new_notes": "  notes verbatim  ",
            },
        }
        return {
            "id": object(),
            "occurred_at": self.occurred_at,
            "customer_id": self.customer_id,
        } | payloads[method_name]

    def test_factory_is_concrete_stateless_and_uses_identity_semantics(self) -> None:
        self.assertFalse(inspect.isabstract(CustomerEventFactory))
        self.assertFalse(hasattr(self.factory, "__dict__"))
        other = CustomerEventFactory()
        self.assertNotEqual(self.factory, other)
        self.assertIs(CustomerEventFactory.__eq__, object.__eq__)
        self.assertIs(CustomerEventFactory.__hash__, object.__hash__)

    def test_constructor_arguments_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            CustomerEventFactory(object())
        with self.assertRaises(TypeError):
            CustomerEventFactory(provider=object())

    def test_public_api_and_keyword_only_signatures_are_exact(self) -> None:
        public = {
            name
            for name, value in vars(CustomerEventFactory).items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public, set(METHOD_CASES))
        for method_name, (event_class, field_names, _) in METHOD_CASES.items():
            with self.subTest(method=method_name):
                signature = inspect.signature(
                    getattr(CustomerEventFactory, method_name),
                    eval_str=True,
                )
                self.assertEqual(tuple(signature.parameters), ("self",) + field_names)
                self.assertEqual(
                    signature.parameters["self"].kind,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
                self.assertTrue(
                    all(
                        signature.parameters[field].kind
                        is inspect.Parameter.KEYWORD_ONLY
                        for field in field_names
                    )
                )
                self.assertIs(signature.return_annotation, event_class)

    def test_argument_errors_are_enforced_by_each_method_signature(self) -> None:
        for method_name in METHOD_CASES:
            method = getattr(self.factory, method_name)
            values = self.kwargs_for(method_name)
            with self.subTest(method=method_name, error="missing"):
                missing_values = values.copy()
                missing_values.pop("id")
                with self.assertRaises(TypeError):
                    method(**missing_values)
            with self.subTest(method=method_name, error="positional"):
                with self.assertRaises(TypeError):
                    method(*values.values())
            with self.subTest(method=method_name, error="unexpected"):
                with self.assertRaises(TypeError):
                    method(**values, unexpected=object())

    def test_exact_events_names_and_values_are_preserved(self) -> None:
        for method_name, (event_class, field_names, event_name) in METHOD_CASES.items():
            values = self.kwargs_for(method_name)
            event = getattr(self.factory, method_name)(**values)
            with self.subTest(method=method_name):
                self.assertIs(type(event), event_class)
                self.assertEqual(event.event_name, event_name)
                for field in field_names:
                    self.assertIs(getattr(event, field), values[field])

    def test_constructor_validation_errors_propagate_unchanged(self) -> None:
        values = self.kwargs_for("create_customer_created")
        for field, invalid in (
            ("id", None),
            ("occurred_at", datetime(2026, 7, 29, 9, 0)),
            ("customer_id", "customer-001"),
            ("name", "Customer One"),
            ("address", "First Address"),
            ("city", "Jakarta"),
            ("notes", object()),
        ):
            with self.subTest(field=field):
                expected_values = values | {field: invalid}
                try:
                    CustomerCreated(
                        event_name="customer.created",
                        **expected_values,
                    )
                except DomainValidationError as expected:
                    with self.assertRaises(DomainValidationError) as actual:
                        self.factory.create_customer_created(**expected_values)
                    self.assertEqual(actual.exception.args, expected.args)
                    self.assertIs(type(actual.exception), type(expected))
                else:
                    self.fail("event constructor did not reject invalid value")

    def test_changed_event_validation_is_delegated(self) -> None:
        for method_name, equal_field in (
            ("create_customer_name_changed", "new_name"),
            ("create_customer_address_changed", "new_address"),
            ("create_customer_city_changed", "new_city"),
            ("create_customer_notes_changed", "new_notes"),
        ):
            values = self.kwargs_for(method_name)
            previous_field = next(
                field for field in values if field.startswith("previous_")
            )
            with self.subTest(method=method_name):
                with self.assertRaises(DomainValidationError):
                    getattr(self.factory, method_name)(
                        **(values | {equal_field: values[previous_field]})
                    )

    def test_dependencies_and_implementation_are_restricted(self) -> None:
        source_path = Path(factory_module.__file__)
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module != "__future__"
        }
        self.assertEqual(
            imports,
            {
                "datetime",
                "core.domain.customer.customer_address",
                "core.domain.customer.customer_city",
                "core.domain.customer.customer_id",
                "core.domain.customer.customer_name",
                "core.domain.customer.events",
            },
        )
        prohibited = (
            "Customer(",
            "AggregateRoot",
            "record_event",
            "pending_events",
            "uuid",
            "datetime.now",
            "datetime.utcnow",
            "EventEnvelope",
            "repository",
            "dispatch",
            "serialize",
            "infrastructure",
        )
        source = source_path.read_text(encoding="utf-8")
        for value in prohibited:
            with self.subTest(value=value):
                self.assertNotIn(value, source)


if __name__ == "__main__":
    unittest.main()
