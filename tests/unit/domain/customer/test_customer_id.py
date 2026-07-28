import ast
import inspect
import unittest
from dataclasses import FrozenInstanceError, dataclass
from pathlib import Path

from core.domain.customer.customer_id import CustomerId
from core.domain.entity import Entity
from core.domain.exceptions import DomainValidationError
from core.domain.value_object import ValueObject


@dataclass(frozen=True)
class OtherId(ValueObject):
    value: str


class CustomerIdTests(unittest.TestCase):
    def test_inherits_from_value_object_and_not_entity(self):
        self.assertTrue(issubclass(CustomerId, ValueObject))
        self.assertFalse(issubclass(CustomerId, Entity))

    def test_valid_string_is_accepted_preserved_and_publicly_readable(self):
        customer_id = CustomerId("customer  001")

        self.assertEqual(customer_id.value, "customer  001")

    def test_construction_requires_exactly_one_externally_supplied_value(self):
        with self.assertRaises(TypeError):
            CustomerId()
        with self.assertRaises(TypeError):
            CustomerId("customer-001", "customer-002")

    def test_non_string_values_are_rejected(self):
        for value in (None, 1, 1.0, True, b"customer-001", [], {}):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    CustomerId(value)

    def test_empty_string_is_rejected(self):
        with self.assertRaises(DomainValidationError):
            CustomerId("")

    def test_whitespace_only_string_is_rejected(self):
        for value in (" ", "\t", "\n", " \t\n"):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    CustomerId(value)

    def test_leading_whitespace_is_rejected_without_trimming(self):
        with self.assertRaises(DomainValidationError):
            CustomerId(" customer-001")

    def test_trailing_whitespace_is_rejected_without_trimming(self):
        with self.assertRaises(DomainValidationError):
            CustomerId("customer-001 ")

    def test_valid_internal_whitespace_is_preserved(self):
        customer_id = CustomerId("customer \t 001")

        self.assertEqual(customer_id.value, "customer \t 001")

    def test_value_cannot_be_changed_after_construction(self):
        customer_id = CustomerId("customer-001")

        with self.assertRaises(FrozenInstanceError):
            customer_id.value = "customer-002"

    def test_equal_values_compare_equal_and_different_values_do_not(self):
        self.assertEqual(CustomerId("customer-001"), CustomerId("customer-001"))
        self.assertNotEqual(CustomerId("customer-001"), CustomerId("customer-002"))

    def test_different_concrete_value_object_type_compares_unequal(self):
        self.assertNotEqual(CustomerId("customer-001"), OtherId("customer-001"))

    def test_equal_instances_have_equal_hashes(self):
        self.assertEqual(
            hash(CustomerId("customer-001")),
            hash(CustomerId("customer-001")),
        )
        self.assertEqual(
            hash(CustomerId("customer-001")),
            hash((CustomerId, "customer-001")),
        )

    def test_can_be_used_as_dictionary_key_and_set_member(self):
        customer_id = CustomerId("customer-001")
        equal_id = CustomerId("customer-001")

        self.assertEqual({customer_id: "customer"}[equal_id], "customer")
        self.assertIn(equal_id, {customer_id})

    def test_no_automatic_identifier_generation_exists(self):
        signature = inspect.signature(CustomerId)

        self.assertEqual(tuple(signature.parameters), ("value",))
        self.assertIs(signature.parameters["value"].default, inspect.Parameter.empty)

    def test_no_unpublished_public_api_exists(self):
        public_fields = {
            name
            for name in CustomerId.__annotations__
            if not name.startswith("_")
        }
        public_behavior = {
            name
            for name in vars(CustomerId)
            if not name.startswith("_") and name not in public_fields
        }

        self.assertEqual(public_fields, {"value"})
        self.assertEqual(public_behavior, set())

    def test_no_prohibited_dependency_exists(self):
        source_path = (
            Path(__file__).parents[4]
            / "core"
            / "domain"
            / "customer"
            / "customer_id.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_roots = {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        imported_modules = {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }

        self.assertEqual(imported_roots | imported_modules, {"dataclasses", "core"})
        prohibited_terms = {
            "uuid",
            "database",
            "serialize",
            "repository",
            "event",
            "customername",
            "customeraddress",
            "customercity",
        }
        source_names = {
            node.id.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        }
        self.assertTrue(prohibited_terms.isdisjoint(source_names))


if __name__ == "__main__":
    unittest.main()
