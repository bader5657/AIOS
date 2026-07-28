import unittest
from abc import ABC
from dataclasses import FrozenInstanceError, dataclass

from core.domain.exceptions import DomainValidationError
from core.domain.value_object import ValueObject


@dataclass(frozen=True)
class Coordinates(ValueObject):
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Label(ValueObject):
    text: str


@dataclass(frozen=True)
class PositiveCount(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise DomainValidationError("value cannot be negative")


class ValueObjectTests(unittest.TestCase):
    def test_same_type_and_components_are_equal(self):
        first = Coordinates(-7.4726, 112.4338)
        second = Coordinates(-7.4726, 112.4338)

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_different_components_are_not_equal(self):
        self.assertNotEqual(
            Coordinates(-7.4726, 112.4338),
            Coordinates(-7.4727, 112.4338),
        )

    def test_different_types_are_not_equal(self):
        self.assertNotEqual(
            Coordinates(-7.4726, 112.4338),
            Label("-7.4726, 112.4338"),
        )

    def test_value_object_cannot_be_changed(self):
        coordinates = Coordinates(-7.4726, 112.4338)

        with self.assertRaises(FrozenInstanceError):
            coordinates.latitude = 0.0

    def test_value_objects_are_dictionary_keys_and_set_members(self):
        first = Coordinates(-7.4726, 112.4338)
        equal = Coordinates(-7.4726, 112.4338)

        self.assertEqual({first: "value"}[equal], "value")
        self.assertIn(equal, {first})

    def test_invalid_construction_can_raise_validation_error(self):
        with self.assertRaises(DomainValidationError):
            PositiveCount(-1)

    def test_base_value_object_is_abstract(self):
        self.assertTrue(issubclass(ValueObject, ABC))
        with self.assertRaises(TypeError):
            ValueObject()

    def test_base_contains_no_customer_or_conversation_behavior(self):
        names = {name.lower() for name in vars(ValueObject)}
        self.assertNotIn("customer", names)
        self.assertNotIn("conversation", names)


if __name__ == "__main__":
    unittest.main()
