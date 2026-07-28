import ast
import inspect
import unittest
from pathlib import Path

from core.domain.aggregate_root import AggregateRoot
from core.domain.customer import Customer, CustomerAddress, CustomerCity, CustomerId, CustomerName
from core.domain.exceptions import DomainValidationError


class CustomerTests(unittest.TestCase):
    def setUp(self):
        self.identity = CustomerId("customer-001")
        self.name = CustomerName("Customer One")
        self.address = CustomerAddress("First Address")
        self.city = CustomerCity("Mojokerto")

    def make(self, notes=None):
        return Customer(self.identity, self.name, self.address, self.city, notes)

    def test_foundation_constructor_and_exact_initial_state(self):
        customer = self.make("  notes  ")
        self.assertIsInstance(customer, AggregateRoot)
        self.assertEqual(tuple(inspect.signature(Customer).parameters), ("customer_id", "name", "address", "city", "notes"))
        self.assertIs(customer.id, self.identity)
        self.assertEqual((customer.name, customer.address, customer.city, customer.notes), (self.name, self.address, self.city, "  notes  "))
        self.assertEqual(customer.pending_events(), ())

    def test_required_fields_and_optional_notes(self):
        with self.assertRaises(TypeError): Customer(self.identity, self.name, self.address)
        self.assertIsNone(self.make().notes)
        self.assertEqual(self.make("").notes, "")
        self.assertIsNone(self.make(None).notes)

    def test_constructor_rejects_incorrect_types(self):
        cases = ((None, self.name, self.address, self.city, None), ("id", self.name, self.address, self.city, None), (self.identity, None, self.address, self.city, None), (self.identity, "name", self.address, self.city, None), (self.identity, self.name, None, self.city, None), (self.identity, self.name, "address", self.city, None), (self.identity, self.name, self.address, None, None), (self.identity, self.name, self.address, "city", None), (self.identity, self.name, self.address, self.city, 1))
        for values in cases:
            with self.subTest(values=values), self.assertRaises(DomainValidationError): Customer(*values)

    def test_fields_are_read_only(self):
        customer = self.make()
        for field, value in (("id", CustomerId("customer-002")), ("name", CustomerName("Other Name")), ("address", CustomerAddress("Other Address")), ("city", CustomerCity("Surabaya")), ("notes", "other")):
            with self.subTest(field=field), self.assertRaises(AttributeError): setattr(customer, field, value)

    def test_updates_change_only_matching_field_and_preserve_identity(self):
        customer = self.make("notes")
        new_name, new_address, new_city = CustomerName("Other Name"), CustomerAddress("Other Address"), CustomerCity("Surabaya")
        for operation, value, field in ((customer.change_name, new_name, "name"), (customer.change_address, new_address, "address"), (customer.change_city, new_city, "city"), (customer.change_notes, "  new notes  ", "notes")):
            before_id = customer.id
            self.assertIsNone(operation(value))
            self.assertIs(getattr(customer, field), value)
            self.assertIs(customer.id, before_id)
            self.assertEqual(customer.pending_events(), ())

    def test_updates_reject_incorrect_types_without_state_change(self):
        customer = self.make("notes")
        original = (customer.id, customer.name, customer.address, customer.city, customer.notes)
        for operation, value in ((customer.change_name, None), (customer.change_name, "name"), (customer.change_address, None), (customer.change_address, "address"), (customer.change_city, None), (customer.change_city, "city"), (customer.change_notes, 1)):
            with self.subTest(operation=operation.__name__), self.assertRaises(DomainValidationError): operation(value)
            self.assertEqual((customer.id, customer.name, customer.address, customer.city, customer.notes), original)

    def test_equal_updates_are_no_ops_and_record_no_event(self):
        customer = self.make("notes")
        original = (customer.name, customer.address, customer.city, customer.notes)
        for operation, value in ((customer.change_name, CustomerName("Customer One")), (customer.change_address, CustomerAddress("First Address")), (customer.change_city, CustomerCity("Mojokerto")), (customer.change_notes, "notes")):
            self.assertIsNone(operation(value))
        self.assertEqual((customer.name, customer.address, customer.city, customer.notes), original)
        self.assertEqual(customer.pending_events(), ())

    def test_identity_equality_hashing_and_duplicates(self):
        equal = Customer(CustomerId("customer-001"), CustomerName("Other Name"), CustomerAddress("Other Address"), CustomerCity("Surabaya"))
        other = Customer(CustomerId("customer-002"), self.name, self.address, self.city)
        self.assertEqual(self.make(), equal)
        self.assertNotEqual(self.make(), other)
        self.assertEqual(hash(self.make()), hash(equal))
        self.assertEqual({self.make(): "customer"}[equal], "customer")
        self.assertEqual((self.make().name, self.make().address, self.make().city), (other.name, other.address, other.city))

    def test_published_api_and_package_exports_only(self):
        public = {name for name in vars(Customer) if not name.startswith("_")}
        self.assertEqual(public, {"name", "address", "city", "notes", "change_name", "change_address", "change_city", "change_notes"})
        import core.domain.customer as package
        self.assertEqual(package.__all__, ("Customer", "CustomerId", "CustomerName", "CustomerAddress", "CustomerCity"))

    def test_no_prohibited_dependencies_or_behavior(self):
        path = Path(__file__).parents[4] / "core/domain/customer/customer.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        names = {node.id.lower() for node in ast.walk(tree) if isinstance(node, ast.Name)} | {node.attr.lower() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        self.assertEqual(modules, {"core"})
        self.assertTrue({"uuid", "datetime", "repository", "database", "persistence", "serialize", "json", "telegram", "record_event"}.isdisjoint(names))
        self.assertTrue({"status", "delete", "deactivate", "archive", "merge", "restore", "created_at", "updated_at", "save", "find"}.isdisjoint(vars(Customer)))


if __name__ == "__main__":
    unittest.main()
