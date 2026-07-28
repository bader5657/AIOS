import unittest
from abc import ABC

from core.domain.entity import Entity
from core.domain.exceptions import DomainValidationError


class ExampleEntity(Entity[str]):
    def __init__(self, entity_id: str) -> None:
        super().__init__(entity_id)


class OtherEntity(Entity[str]):
    def __init__(self, entity_id: str) -> None:
        super().__init__(entity_id)


class EntityTests(unittest.TestCase):
    def test_entity_exposes_its_identity(self):
        entity = ExampleEntity("entity-1")

        self.assertEqual(entity.id, "entity-1")

    def test_none_identity_is_rejected(self):
        with self.assertRaises(DomainValidationError):
            ExampleEntity(None)

    def test_entities_of_same_type_and_identity_are_equal(self):
        first = ExampleEntity("entity-1")
        second = ExampleEntity("entity-1")

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_entities_with_different_identities_are_not_equal(self):
        self.assertNotEqual(
            ExampleEntity("entity-1"),
            ExampleEntity("entity-2"),
        )

    def test_entities_of_different_types_are_not_equal(self):
        self.assertNotEqual(
            ExampleEntity("entity-1"),
            OtherEntity("entity-1"),
        )

    def test_identity_cannot_be_changed(self):
        entity = ExampleEntity("entity-1")

        with self.assertRaises((AttributeError, TypeError)):
            entity.id = "entity-2"

    def test_entity_is_not_equal_to_non_entity(self):
        self.assertNotEqual(ExampleEntity("entity-1"), "entity-1")

    def test_entities_are_dictionary_keys_and_set_members(self):
        first = ExampleEntity("entity-1")
        equal = ExampleEntity("entity-1")

        self.assertEqual({first: "value"}[equal], "value")
        self.assertIn(equal, {first})

    def test_base_entity_is_abstract_and_generates_no_identity(self):
        self.assertTrue(issubclass(Entity, ABC))
        with self.assertRaises(TypeError):
            Entity("entity-1")


if __name__ == "__main__":
    unittest.main()
