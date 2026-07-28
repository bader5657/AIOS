import unittest
from abc import ABC

from core.domain.aggregate_root import AggregateRoot
from core.domain.entity import Entity
from core.domain.exceptions import DomainValidationError


class ExampleAggregateRoot(AggregateRoot[str]):
    def __init__(self, entity_id: str) -> None:
        super().__init__(entity_id)


class OtherAggregateRoot(AggregateRoot[str]):
    def __init__(self, entity_id: str) -> None:
        super().__init__(entity_id)


class AggregateRootTests(unittest.TestCase):
    def test_aggregate_root_inherits_from_entity(self):
        self.assertTrue(issubclass(AggregateRoot, Entity))

    def test_aggregate_root_exposes_supplied_identity(self):
        aggregate = ExampleAggregateRoot("aggregate-1")

        self.assertEqual(aggregate.id, "aggregate-1")

    def test_none_identity_is_rejected(self):
        with self.assertRaises(DomainValidationError):
            ExampleAggregateRoot(None)

    def test_identity_cannot_be_changed(self):
        aggregate = ExampleAggregateRoot("aggregate-1")

        with self.assertRaises((AttributeError, TypeError)):
            aggregate.id = "aggregate-2"

    def test_same_type_and_identity_are_equal(self):
        first = ExampleAggregateRoot("aggregate-1")
        second = ExampleAggregateRoot("aggregate-1")

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_same_type_with_different_identities_are_not_equal(self):
        self.assertNotEqual(
            ExampleAggregateRoot("aggregate-1"),
            ExampleAggregateRoot("aggregate-2"),
        )

    def test_different_types_with_equal_identities_are_not_equal(self):
        self.assertNotEqual(
            ExampleAggregateRoot("aggregate-1"),
            OtherAggregateRoot("aggregate-1"),
        )

    def test_aggregate_roots_are_dictionary_keys_and_set_members(self):
        first = ExampleAggregateRoot("aggregate-1")
        equal = ExampleAggregateRoot("aggregate-1")

        self.assertEqual({first: "value"}[equal], "value")
        self.assertIn(equal, {first})

    def test_base_aggregate_root_is_abstract_and_generates_no_identity(self):
        self.assertTrue(issubclass(AggregateRoot, ABC))
        with self.assertRaises(TypeError):
            AggregateRoot("aggregate-1")

    def test_base_aggregate_root_exposes_only_published_event_api(self):
        public_api = {
            name for name in vars(AggregateRoot) if not name.startswith("_")
        }

        self.assertEqual(
            {"record_event", "pending_events", "pull_events", "clear_events"},
            public_api,
        )

    def test_base_contains_no_customer_or_conversation_behavior(self):
        names = {name.lower() for name in vars(AggregateRoot)}
        self.assertNotIn("customer", names)
        self.assertNotIn("conversation", names)


if __name__ == "__main__":
    unittest.main()
