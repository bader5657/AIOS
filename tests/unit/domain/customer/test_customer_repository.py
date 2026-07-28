import ast
import inspect
import unittest
from pathlib import Path
from typing import get_args, get_origin, get_type_hints

from core.domain.customer.customer import Customer
from core.domain.customer.customer_id import CustomerId
from core.domain.customer.repository import CustomerRepository
from core.domain.repository import AggregateType, Repository
from core.domain.entity import EntityId


class CustomerRepositoryTests(unittest.TestCase):
    OPERATIONS = ("save", "get", "exists", "delete", "list")

    def test_is_exact_customer_repository_specialization(self):
        self.assertTrue(issubclass(CustomerRepository, Repository))
        specializations = [
            base
            for base in CustomerRepository.__orig_bases__
            if get_origin(base) is Repository
        ]
        self.assertEqual(len(specializations), 1)
        self.assertEqual(get_args(specializations[0]), (Customer, CustomerId))

    def test_is_abstract_and_cannot_be_instantiated(self):
        self.assertTrue(inspect.isabstract(CustomerRepository))
        self.assertEqual(
            CustomerRepository.__abstractmethods__,
            set(self.OPERATIONS),
        )
        with self.assertRaises(TypeError):
            CustomerRepository()

    def test_operations_are_inherited_without_redeclaration(self):
        for name in self.OPERATIONS:
            with self.subTest(operation=name):
                self.assertNotIn(name, vars(CustomerRepository))
                self.assertIs(getattr(CustomerRepository, name), getattr(Repository, name))

    def test_exposes_no_additional_public_operation(self):
        public_functions = {
            name
            for name, value in vars(CustomerRepository).items()
            if inspect.isfunction(value) and not name.startswith("_")
        }
        self.assertEqual(public_functions, set())

    def test_inherited_signatures(self):
        expected_parameters = {
            "save": ("self", "aggregate"),
            "get": ("self", "entity_id"),
            "exists": ("self", "entity_id"),
            "delete": ("self", "entity_id"),
            "list": ("self",),
        }
        for name, parameters in expected_parameters.items():
            with self.subTest(operation=name):
                self.assertEqual(
                    tuple(inspect.signature(getattr(CustomerRepository, name)).parameters),
                    parameters,
                )

    def test_effective_specialized_annotations(self):
        substitutions = {AggregateType: Customer, EntityId: CustomerId}

        def specialize(annotation):
            if annotation in substitutions:
                return substitutions[annotation]
            origin = get_origin(annotation)
            if origin is None:
                return annotation
            arguments = tuple(specialize(argument) for argument in get_args(annotation))
            if origin is tuple:
                return tuple[arguments]
            if len(arguments) == 2 and type(None) in arguments:
                other = arguments[0] if arguments[1] is type(None) else arguments[1]
                return other | None
            return annotation

        expected = {
            "save": ({"aggregate": Customer}, type(None)),
            "get": ({"entity_id": CustomerId}, Customer | None),
            "exists": ({"entity_id": CustomerId}, bool),
            "delete": ({"entity_id": CustomerId}, bool),
            "list": ({}, tuple[Customer, ...]),
        }
        for name, (parameters, return_type) in expected.items():
            hints = get_type_hints(getattr(CustomerRepository, name))
            with self.subTest(operation=name):
                for parameter, annotation in parameters.items():
                    self.assertEqual(specialize(hints[parameter]), annotation)
                self.assertEqual(specialize(hints["return"]), return_type)

    def test_all_operations_remain_synchronous_and_abstract(self):
        for name in self.OPERATIONS:
            method = getattr(CustomerRepository, name)
            with self.subTest(operation=name):
                self.assertTrue(getattr(method, "__isabstractmethod__", False))
                self.assertFalse(inspect.iscoroutinefunction(method))

    def test_save_and_duplicate_identity_semantics_are_published(self):
        contract = inspect.getdoc(CustomerRepository)
        self.assertIn("``save`` creates", contract)
        self.assertIn("or updates the single logical entry", contract)
        self.assertIn("returns ``None``", contract)
        self.assertIn("existing ``CustomerId`` replaces that entry", contract)
        self.assertIn("without duplication or a duplicate error", contract)
        self.assertIn("No Customer-field uniqueness", contract)

    def test_get_exists_and_delete_semantics_are_published(self):
        contract = inspect.getdoc(CustomerRepository)
        self.assertIn("matching Customer or ``None`` when missing", contract)
        self.assertIn("whether a matching entry exists without side effects", contract)
        self.assertIn("returns ``True`` when it removes an entry", contract)
        self.assertIn("``False`` for a missing entry", contract)
        self.assertIn("deletion is a no-op", contract)

    def test_list_ordering_and_empty_semantics_are_published(self):
        contract = inspect.getdoc(CustomerRepository)
        self.assertIn("immutable tuple", contract)
        self.assertIn("``Customer.id.value``", contract)
        self.assertIn("ascending Python string order", contract)
        self.assertIn("empty tuple", contract)

    def test_defines_no_constructor_storage_or_concrete_behavior(self):
        self.assertNotIn("__init__", vars(CustomerRepository))
        self.assertEqual(CustomerRepository.__slots__, ())
        self.assertEqual(
            set(vars(CustomerRepository)),
            {
                "__module__",
                "__doc__",
                "__slots__",
                "__orig_bases__",
                "__parameters__",
                "__abstractmethods__",
                "_abc_impl",
            },
        )

    def test_imports_only_published_domain_dependencies(self):
        source_path = Path("core/domain/customer/repository.py")
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imports,
            {
                "core.domain.customer.customer",
                "core.domain.customer.customer_id",
                "core.domain.repository",
            },
        )
        self.assertFalse(any(isinstance(node, (ast.Import, ast.Call)) for node in ast.walk(tree)))
        assignments = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Assign, ast.AnnAssign))
        ]
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0].targets[0].id, "__slots__")

    def test_contains_no_prohibited_api_or_concrete_dependency(self):
        source_path = Path("core/domain/customer/repository.py")
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        class_node = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "CustomerRepository"
        )
        prohibited_operations = {
            "find_by_name", "search", "filter", "paginate", "count"
        }
        methods = {
            node.name
            for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertTrue(methods.isdisjoint(prohibited_operations))
        self.assertEqual(methods, set())
        self.assertFalse(
            any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                for node in class_node.body
            )
        )


if __name__ == "__main__":
    unittest.main()
