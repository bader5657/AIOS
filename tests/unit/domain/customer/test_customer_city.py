import ast
import inspect
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from core.domain.customer.customer_address import CustomerAddress
from core.domain.customer.customer_city import CustomerCity
from core.domain.entity import Entity
from core.domain.exceptions import DomainValidationError
from core.domain.value_object import ValueObject


class CustomerCityTests(unittest.TestCase):
    def test_foundation_and_valid_value_contract(self):
        self.assertTrue(issubclass(CustomerCity, ValueObject))
        self.assertFalse(issubclass(CustomerCity, Entity))
        self.assertEqual(CustomerCity("New  York").value, "New  York")

    def test_construction_requires_exactly_one_value(self):
        with self.assertRaises(TypeError):
            CustomerCity()
        with self.assertRaises(TypeError):
            CustomerCity("AB", "CD")

    def test_non_string_empty_and_whitespace_only_values_are_rejected(self):
        for value in (None, 1, 1.0, True, b"AB", [], {}, "", " ", "\t", "\n"):
            with self.subTest(value=value), self.assertRaises(DomainValidationError):
                CustomerCity(value)

    def test_boundary_whitespace_is_rejected(self):
        for value in (" AB", "AB ", "\tAB", "AB\n"):
            with self.subTest(value=value), self.assertRaises(DomainValidationError):
                CustomerCity(value)

    def test_internal_whitespace_is_preserved(self):
        self.assertEqual(CustomerCity("A \t B").value, "A \t B")

    def test_minimum_length_is_enforced(self):
        with self.assertRaises(DomainValidationError):
            CustomerCity("A")
        self.assertEqual(CustomerCity("AB").value, "AB")

    def test_value_is_immutable(self):
        value = CustomerCity("Mojokerto")
        with self.assertRaises(FrozenInstanceError):
            value.value = "Surabaya"

    def test_equality_hashing_and_collection_contract(self):
        value = CustomerCity("Mojokerto")
        equal = CustomerCity("Mojokerto")
        self.assertEqual(value, equal)
        self.assertNotEqual(value, CustomerCity("Surabaya"))
        self.assertNotEqual(CustomerAddress("Mojokerto"), value)
        self.assertEqual(hash(value), hash(equal))
        self.assertEqual(hash(value), hash((CustomerCity, "Mojokerto")))
        self.assertEqual({value: "customer"}[equal], "customer")
        self.assertIn(equal, {value})

    def test_no_normalization_occurs(self):
        self.assertEqual(CustomerCity("McMURDO  Town").value, "McMURDO  Town")

    def test_no_unpublished_public_api_exists(self):
        self.assertEqual(tuple(inspect.signature(CustomerCity).parameters), ("value",))
        fields = {name for name in CustomerCity.__annotations__ if not name.startswith("_")}
        behavior = {name for name in vars(CustomerCity) if not name.startswith("_") and name not in fields}
        self.assertEqual(fields, {"value"})
        self.assertEqual(behavior, set())

    def test_no_prohibited_dependency_exists(self):
        path = Path(__file__).parents[4] / "core/domain/customer/customer_city.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(modules, {"dataclasses", "core"})
        prohibited = {"repository", "database", "event", "serialize", "json", "telegram"}
        names = {node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertTrue(prohibited.isdisjoint(names))


if __name__ == "__main__":
    unittest.main()
