import ast
import inspect
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.customer.customer_name import CustomerName
from core.domain.entity import Entity
from core.domain.exceptions import DomainValidationError
from core.domain.value_object import ValueObject


class CustomerAddressTests(unittest.TestCase):
    def test_foundation_and_valid_value_contract(self):
        self.assertTrue(issubclass(CustomerAddress, ValueObject))
        self.assertFalse(issubclass(CustomerAddress, Entity))
        self.assertEqual(CustomerAddress("Main  Street").value, "Main  Street")

    def test_construction_requires_exactly_one_value(self):
        with self.assertRaises(TypeError):
            CustomerAddress()
        with self.assertRaises(TypeError):
            CustomerAddress("First", "Second")

    def test_non_string_empty_and_whitespace_only_values_are_rejected(self):
        for value in (None, 1, 1.0, True, b"First", [], {}, "", " ", "\t", "\n"):
            with self.subTest(value=value), self.assertRaises(DomainValidationError):
                CustomerAddress(value)

    def test_boundary_whitespace_is_rejected(self):
        for value in (" First", "First ", "\tFirst", "First\n"):
            with self.subTest(value=value), self.assertRaises(DomainValidationError):
                CustomerAddress(value)

    def test_internal_whitespace_is_preserved(self):
        self.assertEqual(CustomerAddress("12 \t Road").value, "12 \t Road")

    def test_minimum_length_is_enforced(self):
        for value in ("A", "AB", "ABC", "ABCD"):
            with self.subTest(value=value), self.assertRaises(DomainValidationError):
                CustomerAddress(value)
        self.assertEqual(CustomerAddress("ABCDE").value, "ABCDE")

    def test_value_is_immutable(self):
        value = CustomerAddress("Valid Address")
        with self.assertRaises(FrozenInstanceError):
            value.value = "Other Address"

    def test_equality_hashing_and_collection_contract(self):
        value = CustomerAddress("Valid Address")
        equal = CustomerAddress("Valid Address")
        self.assertEqual(value, equal)
        self.assertNotEqual(value, CustomerAddress("Other Address"))
        self.assertNotEqual(CustomerName("Valid Name"), CustomerAddress("Valid Name"))
        self.assertNotEqual(CustomerAddress("Mojokerto"), CustomerCity("Mojokerto"))
        self.assertEqual(hash(value), hash(equal))
        self.assertEqual(hash(value), hash((CustomerAddress, "Valid Address")))
        self.assertEqual({value: "customer"}[equal], "customer")
        self.assertIn(equal, {value})

    def test_no_normalization_occurs(self):
        self.assertEqual(CustomerAddress("Jl. MIXED  Case").value, "Jl. MIXED  Case")

    def test_no_unpublished_public_api_exists(self):
        self.assertEqual(tuple(inspect.signature(CustomerAddress).parameters), ("value",))
        fields = {name for name in CustomerAddress.__annotations__ if not name.startswith("_")}
        behavior = {name for name in vars(CustomerAddress) if not name.startswith("_") and name not in fields}
        self.assertEqual(fields, {"value"})
        self.assertEqual(behavior, set())

    def test_no_prohibited_dependency_exists(self):
        path = Path(__file__).parents[4] / "core/domain/customer/customer_address.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(modules, {"dataclasses", "core"})
        prohibited = {"repository", "database", "event", "serialize", "json", "telegram"}
        names = {node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertTrue(prohibited.isdisjoint(names))


if __name__ == "__main__":
    unittest.main()
