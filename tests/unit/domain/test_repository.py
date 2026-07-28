import inspect
import unittest
from abc import ABC
from typing import Generic, TypeVar, get_args, get_origin, get_type_hints

from core.domain.aggregate_root import AggregateRoot
from core.domain.entity import EntityId
from core.domain.repository import AggregateType, Repository


class RepositoryTests(unittest.TestCase):
    def test_repository_is_abstract_and_cannot_be_instantiated(self):
        self.assertTrue(issubclass(Repository, ABC))
        self.assertEqual(
            Repository.__abstractmethods__,
            {"save", "get", "exists", "delete", "list"},
        )

        with self.assertRaises(TypeError):
            Repository()

    def test_repository_exposes_exactly_the_published_operations(self):
        operations = {
            name
            for name, value in vars(Repository).items()
            if inspect.isfunction(value) and not name.startswith("_")
        }

        self.assertEqual(operations, {"save", "get", "exists", "delete", "list"})

    def test_save_signature(self):
        signature = inspect.signature(Repository.save)
        hints = get_type_hints(Repository.save)

        self.assertEqual(tuple(signature.parameters), ("self", "aggregate"))
        self.assertIs(hints["aggregate"], AggregateType)
        self.assertIs(hints["return"], type(None))

    def test_get_signature(self):
        signature = inspect.signature(Repository.get)
        hints = get_type_hints(Repository.get)

        self.assertEqual(tuple(signature.parameters), ("self", "entity_id"))
        self.assertIs(hints["entity_id"], EntityId)
        self.assertEqual(get_args(hints["return"]), (AggregateType, type(None)))

    def test_exists_signature(self):
        signature = inspect.signature(Repository.exists)
        hints = get_type_hints(Repository.exists)

        self.assertEqual(tuple(signature.parameters), ("self", "entity_id"))
        self.assertIs(hints["entity_id"], EntityId)
        self.assertIs(hints["return"], bool)

    def test_delete_signature(self):
        signature = inspect.signature(Repository.delete)
        hints = get_type_hints(Repository.delete)

        self.assertEqual(tuple(signature.parameters), ("self", "entity_id"))
        self.assertIs(hints["entity_id"], EntityId)
        self.assertIs(hints["return"], bool)

    def test_list_signature_returns_immutable_tuple_type(self):
        signature = inspect.signature(Repository.list)
        return_type = get_type_hints(Repository.list)["return"]

        self.assertEqual(tuple(signature.parameters), ("self",))
        self.assertIs(get_origin(return_type), tuple)
        self.assertEqual(get_args(return_type), (AggregateType, Ellipsis))

    def test_repository_has_correct_generic_typing(self):
        self.assertTrue(issubclass(Repository, Generic))
        self.assertEqual(Repository.__parameters__, (AggregateType, EntityId))
        self.assertIs(AggregateType.__bound__, AggregateRoot)

    def test_all_operations_are_synchronous_and_abstract(self):
        for name in ("save", "get", "exists", "delete", "list"):
            method = getattr(Repository, name)
            with self.subTest(method=name):
                self.assertTrue(getattr(method, "__isabstractmethod__", False))
                self.assertFalse(inspect.iscoroutinefunction(method))

    def test_repository_contains_no_prohibited_apis(self):
        names = {name.lower() for name in vars(Repository)}
        prohibited = {
            "postgresql",
            "sqlalchemy",
            "orm",
            "sql",
            "filesystem",
            "serialization",
            "json",
            "telegram",
            "infrastructure",
            "adapter",
            "framework",
            "domain_event",
            "domain_events",
            "customer",
            "conversation",
            "entitynotfounderror",
        }

        self.assertTrue(names.isdisjoint(prohibited))

    def test_repository_defines_no_storage_or_persistence_state(self):
        self.assertEqual(Repository.__slots__, ())
        self.assertNotIn("__init__", vars(Repository))


if __name__ == "__main__":
    unittest.main()
