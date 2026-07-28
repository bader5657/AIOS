"""Tests for the published base DomainEvent contract."""

from abc import ABC
from datetime import datetime, timezone
import inspect
from pathlib import Path
import unittest

from core.domain.domain_event import DomainEvent
from core.domain.exceptions import DomainValidationError


class TestEvent(DomainEvent):
    __slots__ = ()

    def __init__(
        self,
        id: object,
        occurred_at: datetime,
        event_name: str,
    ) -> None:
        super().__init__(id, occurred_at, event_name)


class OtherTestEvent(DomainEvent):
    __slots__ = ()

    def __init__(
        self,
        id: object,
        occurred_at: datetime,
        event_name: str,
    ) -> None:
        super().__init__(id, occurred_at, event_name)


class DomainEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.occurred_at = datetime(2026, 7, 28, 8, 30, tzinfo=timezone.utc)

    def make_event(
        self,
        id: object = "event-1",
        occurred_at: object = None,
        event_name: object = "test.occurred",
    ) -> TestEvent:
        timestamp = self.occurred_at if occurred_at is None else occurred_at
        return TestEvent(id, timestamp, event_name)

    def test_domain_event_is_abstract(self) -> None:
        self.assertTrue(issubclass(DomainEvent, ABC))
        self.assertTrue(inspect.isabstract(DomainEvent))

    def test_domain_event_cannot_be_instantiated_directly(self) -> None:
        with self.assertRaises(TypeError):
            DomainEvent("event-1", self.occurred_at, "test.occurred")

    def test_concrete_event_exposes_supplied_values(self) -> None:
        event = self.make_event()

        self.assertEqual("event-1", event.id)
        self.assertIs(self.occurred_at, event.occurred_at)
        self.assertEqual("test.occurred", event.event_name)

    def test_none_id_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            self.make_event(id=None)

    def test_none_occurred_at_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            TestEvent("event-1", None, "test.occurred")

    def test_non_datetime_occurred_at_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            self.make_event(occurred_at="2026-07-28")

    def test_naive_datetime_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            self.make_event(occurred_at=datetime(2026, 7, 28, 8, 30))

    def test_timezone_aware_datetime_is_accepted(self) -> None:
        event = self.make_event()

        self.assertIs(self.occurred_at, event.occurred_at)

    def test_non_string_event_name_is_rejected(self) -> None:
        for value in (None, 123, object()):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    self.make_event(event_name=value)

    def test_empty_event_name_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            self.make_event(event_name="")

    def test_whitespace_only_event_name_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            self.make_event(event_name=" \t\n ")

    def test_event_name_is_not_normalized(self) -> None:
        event = self.make_event(event_name="  test.occurred  ")

        self.assertEqual("  test.occurred  ", event.event_name)

    def test_all_fields_are_immutable(self) -> None:
        event = self.make_event()

        for name, value in (
            ("id", "event-2"),
            ("occurred_at", datetime.now(timezone.utc)),
            ("event_name", "test.changed"),
            ("_id", "event-2"),
            ("_occurred_at", datetime.now(timezone.utc)),
            ("_event_name", "test.changed"),
        ):
            with self.subTest(name=name):
                with self.assertRaises(AttributeError):
                    setattr(event, name, value)

    def test_equal_events_have_equal_hashes(self) -> None:
        first = self.make_event()
        second = self.make_event()

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_any_differing_field_makes_events_unequal(self) -> None:
        event = self.make_event()
        later = datetime(2026, 7, 28, 8, 31, tzinfo=timezone.utc)

        differing_events = (
            self.make_event(id="event-2"),
            self.make_event(occurred_at=later),
            self.make_event(event_name="test.changed"),
        )
        for other in differing_events:
            with self.subTest(other=other):
                self.assertNotEqual(event, other)

    def test_different_concrete_types_are_unequal(self) -> None:
        event = self.make_event()
        other = OtherTestEvent(
            event.id,
            event.occurred_at,
            event.event_name,
        )

        self.assertNotEqual(event, other)

    def test_non_event_is_unequal(self) -> None:
        self.assertNotEqual(self.make_event(), object())

    def test_events_are_dictionary_keys_and_set_members(self) -> None:
        event = self.make_event()
        equal_event = self.make_event()

        self.assertEqual("value", {event: "value"}[equal_event])
        self.assertIn(equal_event, {event})

    def test_no_unpublished_public_api_exists(self) -> None:
        public_api = {
            name
            for name in vars(DomainEvent)
            if not name.startswith("_")
        }

        self.assertEqual({"id", "occurred_at", "event_name"}, public_api)

    def test_no_prohibited_dependencies_or_apis_exist(self) -> None:
        source_path = (
            Path(__file__).parents[3] / "core" / "domain" / "domain_event.py"
        )
        source = source_path.read_text(encoding="utf-8").lower()
        prohibited = (
            "aggregate_root",
            "repository",
            "eventenvelope",
            "eventexposure",
            "event_bus",
            "dispatcher",
            "publisher",
            "handler",
            "persistence",
            "serialization",
            "json",
            "postgres",
            "customer",
            "conversation",
            "adapter",
            "infrastructure",
            "framework",
            "payload",
            "metadata",
            "aggregate_id",
            "correlation_id",
            "causation_id",
            "version",
            "source",
        )

        for symbol in prohibited:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, source)


if __name__ == "__main__":
    unittest.main()
