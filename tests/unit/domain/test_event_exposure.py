"""Tests for the published AggregateRoot Event Exposure contract."""

from datetime import datetime, timezone
import ast
import inspect
from pathlib import Path
import unittest
from typing import get_type_hints

from core.domain.aggregate_root import AggregateRoot
from core.domain.domain_event import DomainEvent
from core.domain.exceptions import DomainValidationError


class ExampleAggregateRoot(AggregateRoot[str]):
    __slots__ = ()

    def __init__(self, entity_id: str) -> None:
        super().__init__(entity_id)


class TestEvent(DomainEvent):
    __slots__ = ()

    def __init__(self, event_id: object = "event-1") -> None:
        super().__init__(
            event_id,
            datetime(2026, 7, 28, 8, 30, tzinfo=timezone.utc),
            "test.occurred",
        )


class AggregateRootEventExposureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.aggregate = ExampleAggregateRoot("aggregate-1")

    def test_new_aggregate_has_no_pending_events(self) -> None:
        self.assertEqual((), self.aggregate.pending_events())

    def test_pending_events_initially_returns_empty_tuple(self) -> None:
        events = self.aggregate.pending_events()

        self.assertIsInstance(events, tuple)
        self.assertEqual((), events)

    def test_pull_events_initially_returns_empty_tuple(self) -> None:
        events = self.aggregate.pull_events()

        self.assertIsInstance(events, tuple)
        self.assertEqual((), events)

    def test_clear_events_is_safe_on_empty_aggregate(self) -> None:
        self.assertIsNone(self.aggregate.clear_events())
        self.assertEqual((), self.aggregate.pending_events())

    def test_record_event_accepts_domain_event_and_returns_none(self) -> None:
        event = TestEvent()

        self.assertIsNone(self.aggregate.record_event(event))
        self.assertEqual((event,), self.aggregate.pending_events())

    def test_record_event_rejects_none(self) -> None:
        with self.assertRaises(DomainValidationError):
            self.aggregate.record_event(None)

    def test_record_event_rejects_non_domain_event_values(self) -> None:
        for value in (object(), "event", 1, {}, []):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    self.aggregate.record_event(value)

        self.assertEqual((), self.aggregate.pending_events())

    def test_one_event_is_exposed_through_pending_events(self) -> None:
        event = TestEvent()
        self.aggregate.record_event(event)

        self.assertEqual((event,), self.aggregate.pending_events())

    def test_multiple_events_preserve_insertion_order(self) -> None:
        events = (TestEvent("event-1"), TestEvent("event-2"), TestEvent("event-3"))
        for event in events:
            self.aggregate.record_event(event)

        self.assertEqual(events, self.aggregate.pending_events())

    def test_duplicate_and_equal_events_are_preserved(self) -> None:
        event = TestEvent()
        equal_event = TestEvent()
        for recorded in (event, event, equal_event):
            self.aggregate.record_event(recorded)

        exposed = self.aggregate.pending_events()
        self.assertEqual((event, event, equal_event), exposed)
        self.assertIs(exposed[0], exposed[1])
        self.assertIsNot(exposed[1], exposed[2])

    def test_pending_events_returns_tuple_without_clearing(self) -> None:
        event = TestEvent()
        self.aggregate.record_event(event)

        first = self.aggregate.pending_events()
        second = self.aggregate.pending_events()

        self.assertIsInstance(first, tuple)
        self.assertEqual((event,), first)
        self.assertEqual(first, second)

    def test_returned_tuple_cannot_mutate_internal_state(self) -> None:
        event = TestEvent()
        self.aggregate.record_event(event)
        snapshot = self.aggregate.pending_events()

        with self.assertRaises(TypeError):
            snapshot[0] = TestEvent("replacement")

        extended = snapshot + (TestEvent("event-2"),)
        self.assertEqual(2, len(extended))
        self.assertEqual((event,), self.aggregate.pending_events())

    def test_pull_events_returns_tuple_in_order_and_clears(self) -> None:
        events = (TestEvent("event-1"), TestEvent("event-2"))
        for event in events:
            self.aggregate.record_event(event)

        pulled = self.aggregate.pull_events()

        self.assertIsInstance(pulled, tuple)
        self.assertEqual(events, pulled)
        self.assertEqual((), self.aggregate.pending_events())

    def test_second_pull_without_new_events_returns_empty_tuple(self) -> None:
        event = TestEvent()
        self.aggregate.record_event(event)

        self.assertEqual((event,), self.aggregate.pull_events())
        self.assertEqual((), self.aggregate.pull_events())

    def test_clear_events_removes_all_events_and_returns_none(self) -> None:
        self.aggregate.record_event(TestEvent("event-1"))
        self.aggregate.record_event(TestEvent("event-2"))

        self.assertIsNone(self.aggregate.clear_events())
        self.assertEqual((), self.aggregate.pending_events())

    def test_new_events_can_be_recorded_after_pull(self) -> None:
        first = TestEvent("event-1")
        second = TestEvent("event-2")
        self.aggregate.record_event(first)
        self.aggregate.pull_events()

        self.aggregate.record_event(second)

        self.assertEqual((second,), self.aggregate.pending_events())

    def test_new_events_can_be_recorded_after_clear(self) -> None:
        first = TestEvent("event-1")
        second = TestEvent("event-2")
        self.aggregate.record_event(first)
        self.aggregate.clear_events()

        self.aggregate.record_event(second)

        self.assertEqual((second,), self.aggregate.pending_events())

    def test_record_pull_and_clear_do_not_mutate_events(self) -> None:
        event = TestEvent()
        original = (event.id, event.occurred_at, event.event_name, hash(event))

        self.aggregate.record_event(event)
        self.assertIs(event, self.aggregate.pending_events()[0])
        self.assertIs(event, self.aggregate.pull_events()[0])
        self.aggregate.record_event(event)
        self.aggregate.clear_events()

        self.assertEqual(
            original,
            (event.id, event.occurred_at, event.event_name, hash(event)),
        )

    def test_pending_collection_is_private(self) -> None:
        self.assertFalse(hasattr(self.aggregate, "events"))
        self.assertFalse(hasattr(self.aggregate, "pending_event_collection"))
        self.assertEqual(("__pending_events",), AggregateRoot.__slots__)
        self.assertTrue(hasattr(self.aggregate, "_AggregateRoot__pending_events"))

    def test_only_published_public_api_exists(self) -> None:
        public_api = {
            name for name in vars(AggregateRoot) if not name.startswith("_")
        }

        self.assertEqual(
            {"record_event", "pending_events", "pull_events", "clear_events"},
            public_api,
        )

    def test_published_signatures_are_exact(self) -> None:
        record_signature = inspect.signature(AggregateRoot.record_event)
        self.assertEqual(("self", "event"), tuple(record_signature.parameters))
        self.assertEqual(DomainEvent, get_type_hints(AggregateRoot.record_event)["event"])
        self.assertIs(type(None), get_type_hints(AggregateRoot.record_event)["return"])

        for method_name in ("pending_events", "pull_events"):
            method = getattr(AggregateRoot, method_name)
            self.assertEqual(("self",), tuple(inspect.signature(method).parameters))
            self.assertEqual(
                tuple[DomainEvent, ...],
                get_type_hints(method)["return"],
            )

        self.assertEqual(
            ("self",),
            tuple(inspect.signature(AggregateRoot.clear_events).parameters),
        )
        self.assertIs(
            type(None),
            get_type_hints(AggregateRoot.clear_events)["return"],
        )

    def test_no_envelope_dispatch_persistence_or_prohibited_dependency(self) -> None:
        source_path = (
            Path(__file__).parents[3] / "core" / "domain" / "aggregate_root.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }

        self.assertEqual(
            {
                "__future__",
                "abc",
                "core.domain.domain_event",
                "core.domain.entity",
                "core.domain.exceptions",
            },
            imported_modules,
        )
        self.assertTrue(
            imported_names.isdisjoint(
                {
                    "EventEnvelope",
                    "dispatcher",
                    "publisher",
                    "persistence",
                    "retry",
                    "serialization",
                    "infrastructure",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
