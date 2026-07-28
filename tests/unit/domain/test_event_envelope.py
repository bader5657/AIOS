"""Tests for the published base EventEnvelope contract."""

from datetime import datetime, timezone
import ast
from pathlib import Path
import unittest

from core.domain.domain_event import DomainEvent
from core.domain.event_envelope import EventEnvelope
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


class OtherEnvelope(EventEnvelope):
    __slots__ = ()


class EventEnvelopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.timestamp = datetime(2026, 7, 28, 9, 0, tzinfo=timezone.utc)
        self.event = TestEvent(
            "event-1", self.timestamp, "test.occurred"
        )

    def make_envelope(
        self,
        event: object = None,
        aggregate_id: object = "aggregate-1",
        correlation_id: object = "correlation-1",
        causation_id: object = "causation-1",
        schema_version: object = 1,
    ) -> EventEnvelope:
        wrapped_event = self.event if event is None else event
        return EventEnvelope(
            wrapped_event,
            aggregate_id,
            correlation_id,
            causation_id,
            schema_version=schema_version,
        )

    def test_valid_domain_event_is_required(self) -> None:
        with self.assertRaises(TypeError):
            EventEnvelope(schema_version=1)

        self.assertIs(self.event, self.make_envelope().event)

    def test_none_event_is_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            EventEnvelope(None, schema_version=1)

    def test_non_domain_event_is_rejected(self) -> None:
        for value in (object(), "event", 1):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    EventEnvelope(value, schema_version=1)

    def test_event_property_returns_wrapped_event(self) -> None:
        self.assertIs(self.event, self.make_envelope().event)

    def test_mirrored_fields_exactly_return_event_fields(self) -> None:
        envelope = self.make_envelope()

        self.assertIs(self.event.id, envelope.event_id)
        self.assertIs(self.event.event_name, envelope.event_name)
        self.assertIs(self.event.occurred_at, envelope.occurred_at)
        self.assertIsNotNone(envelope.occurred_at.utcoffset())

    def test_mirrored_fields_cannot_be_supplied(self) -> None:
        for field in ("event_id", "event_name", "occurred_at"):
            with self.subTest(field=field):
                with self.assertRaises(TypeError):
                    EventEnvelope(
                        self.event, schema_version=1, **{field: object()}
                    )

    def test_optional_identity_fields_accept_and_preserve_none(self) -> None:
        envelope = EventEnvelope(self.event, schema_version=1)

        self.assertIsNone(envelope.aggregate_id)
        self.assertIsNone(envelope.correlation_id)
        self.assertIsNone(envelope.causation_id)

    def test_optional_identity_fields_preserve_supplied_values(self) -> None:
        aggregate_id = object()
        correlation_id = object()
        causation_id = object()
        envelope = EventEnvelope(
            self.event,
            aggregate_id,
            correlation_id,
            causation_id,
            schema_version=1,
        )

        self.assertIs(aggregate_id, envelope.aggregate_id)
        self.assertIs(correlation_id, envelope.correlation_id)
        self.assertIs(causation_id, envelope.causation_id)

    def test_schema_version_is_required(self) -> None:
        with self.assertRaises(TypeError):
            EventEnvelope(self.event)

    def test_schema_version_accepts_positive_integers(self) -> None:
        for value in (1, 2, 100):
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    EventEnvelope(self.event, schema_version=value).schema_version,
                )

    def test_schema_version_rejects_zero_and_negative_integers(self) -> None:
        for value in (0, -1, -100):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    EventEnvelope(self.event, schema_version=value)

    def test_schema_version_rejects_non_integers_and_bool(self) -> None:
        for value in (True, False, None, 1.0, "1", object()):
            with self.subTest(value=value):
                with self.assertRaises(DomainValidationError):
                    EventEnvelope(self.event, schema_version=value)

    def test_all_fields_are_immutable(self) -> None:
        envelope = self.make_envelope()
        replacements = {
            "event": self.event,
            "event_id": "event-2",
            "event_name": "test.changed",
            "occurred_at": datetime.now(timezone.utc),
            "aggregate_id": "aggregate-2",
            "correlation_id": "correlation-2",
            "causation_id": "causation-2",
            "schema_version": 2,
            "_event": self.event,
            "_aggregate_id": "aggregate-2",
            "_correlation_id": "correlation-2",
            "_causation_id": "causation-2",
            "_schema_version": 2,
        }

        for name, value in replacements.items():
            with self.subTest(name=name):
                with self.assertRaises(AttributeError):
                    setattr(envelope, name, value)

    def test_same_concrete_type_and_equality_fields_compare_equal(self) -> None:
        equal_event = TestEvent(
            self.event.id, self.event.occurred_at, self.event.event_name
        )

        self.assertEqual(self.make_envelope(), self.make_envelope(equal_event))

    def test_changing_any_equality_field_makes_envelopes_unequal(self) -> None:
        baseline = self.make_envelope()
        changed_event = TestEvent(
            "event-2", self.timestamp, "test.occurred"
        )
        changed = (
            self.make_envelope(event=changed_event),
            self.make_envelope(aggregate_id="aggregate-2"),
            self.make_envelope(correlation_id="correlation-2"),
            self.make_envelope(causation_id="causation-2"),
            self.make_envelope(schema_version=2),
        )

        for envelope in changed:
            with self.subTest(envelope=envelope):
                self.assertNotEqual(baseline, envelope)

    def test_different_concrete_envelope_types_compare_unequal(self) -> None:
        envelope = self.make_envelope()
        other = OtherEnvelope(
            self.event,
            "aggregate-1",
            "correlation-1",
            "causation-1",
            schema_version=1,
        )

        self.assertNotEqual(envelope, other)

    def test_non_envelope_value_compares_unequal(self) -> None:
        self.assertNotEqual(self.make_envelope(), object())

    def test_equal_envelopes_have_equal_hashes(self) -> None:
        first = self.make_envelope()
        second = self.make_envelope()

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_envelopes_are_dictionary_keys_and_set_members(self) -> None:
        envelope = self.make_envelope()
        equal_envelope = self.make_envelope()

        self.assertEqual("value", {envelope: "value"}[equal_envelope])
        self.assertIn(equal_envelope, {envelope})

    def test_no_unpublished_public_api_exists(self) -> None:
        public_api = {
            name
            for name in vars(EventEnvelope)
            if not name.startswith("_")
        }

        self.assertEqual(
            {
                "event",
                "event_id",
                "event_name",
                "occurred_at",
                "aggregate_id",
                "correlation_id",
                "causation_id",
                "schema_version",
            },
            public_api,
        )

    def test_no_prohibited_dependency_or_behavior_exists(self) -> None:
        source_path = (
            Path(__file__).parents[3]
            / "core"
            / "domain"
            / "event_envelope.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

        self.assertTrue(
            imports
            <= {
                "annotations",
                "datetime",
                "Any",
                "DomainEvent",
                "DomainValidationError",
            }
        )
        self.assertFalse(
            calls
            & {
                "uuid4",
                "datetime.now",
                "datetime.utcnow",
                "json",
                "dict",
            }
        )


if __name__ == "__main__":
    unittest.main()
