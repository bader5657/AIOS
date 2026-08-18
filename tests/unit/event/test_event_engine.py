"""Contract tests for the fresh in-memory Event Engine runtime."""

from __future__ import annotations

import ast
import asyncio
from datetime import datetime, timezone
from pathlib import Path
import unittest

import core.event as event_module
from core.domain.domain_event import DomainEvent
from core.domain.event_envelope import EventEnvelope
from core.event import (
    EventDeliveryFailureCode,
    EventDeliveryResult,
    EventEngine,
    EventEngineRegistrationError,
)


class SampleEvent(DomainEvent):
    __slots__ = ()

    def __init__(self, event_name: str = "test.occurred") -> None:
        super().__init__(
            "event-1",
            datetime(2026, 8, 18, 9, 0, tzinfo=timezone.utc),
            event_name,
        )


def make_envelope(event_name: str = "test.occurred") -> EventEnvelope:
    return EventEnvelope(SampleEvent(event_name), schema_version=1)


class EventEngineTests(unittest.IsolatedAsyncioTestCase):
    def test_constructs_with_no_public_historical_api(self) -> None:
        engine = EventEngine()

        self.assertFalse(hasattr(engine, "dispatch"))
        self.assertFalse(hasattr(engine, "emit"))
        self.assertFalse(hasattr(engine, "publish"))
        self.assertFalse(hasattr(engine, "unregister"))
        self.assertFalse(hasattr(engine, "registry"))
        self.assertFalse(hasattr(event_module, "Event"))
        self.assertFalse(hasattr(event_module, "EventDispatcher"))
        self.assertFalse(hasattr(event_module, "EventRegistry"))

    async def test_one_registered_handler_returns_exact_success_result(self) -> None:
        engine = EventEngine()
        received: list[EventEnvelope] = []

        async def handler(envelope: EventEnvelope) -> None:
            received.append(envelope)

        envelope = make_envelope()
        engine.register(envelope.event_name, handler)

        result = await engine.process(envelope)

        self.assertEqual([envelope], received)
        self.assertEqual(
            EventDeliveryResult(True, 1, None, None),
            result,
        )

    async def test_invalid_envelope_returns_bounded_failure_without_handler(self) -> None:
        engine = EventEngine()
        calls = 0

        async def handler(envelope: EventEnvelope) -> None:
            nonlocal calls
            calls += 1

        engine.register("test.occurred", handler)

        result = await engine.process(object())  # type: ignore[arg-type]

        self.assertFalse(result.success)
        self.assertEqual(0, result.delivered_handler_count)
        self.assertIs(
            EventDeliveryFailureCode.INVALID_ENVELOPE,
            result.failure_code,
        )
        self.assertTrue(result.failure_reason)
        self.assertEqual(0, calls)

        valid_result = await engine.process(make_envelope())

        self.assertTrue(valid_result.success)
        self.assertEqual(1, valid_result.delivered_handler_count)
        self.assertEqual(1, calls)

    async def test_no_handler_is_a_bounded_failure_not_silent_success(self) -> None:
        engine = EventEngine()
        envelope = make_envelope()
        calls = 0

        result = await engine.process(envelope)

        self.assertFalse(result.success)
        self.assertEqual(0, result.delivered_handler_count)
        self.assertIs(EventDeliveryFailureCode.NO_HANDLER, result.failure_code)
        self.assertTrue(result.failure_reason)

        async def handler(received: EventEnvelope) -> None:
            nonlocal calls
            self.assertIs(envelope, received)
            calls += 1

        engine.register(envelope.event_name, handler)
        later_result = await engine.process(envelope)

        self.assertTrue(later_result.success)
        self.assertEqual(1, later_result.delivered_handler_count)
        self.assertEqual(1, calls)

    async def test_handlers_are_awaited_sequentially_in_registration_order(self) -> None:
        engine = EventEngine()
        sequence: list[str] = []

        async def first(envelope: EventEnvelope) -> None:
            sequence.append("a-start")
            await asyncio.sleep(0)
            sequence.append("a-end")

        async def second(envelope: EventEnvelope) -> None:
            self.assertEqual("a-end", sequence[-1])
            sequence.append("b-start")
            await asyncio.sleep(0)
            sequence.append("b-end")

        async def third(envelope: EventEnvelope) -> None:
            self.assertEqual("b-end", sequence[-1])
            sequence.append("c-start")
            await asyncio.sleep(0)
            sequence.append("c-end")

        for handler in (first, second, third):
            engine.register("test.occurred", handler)

        result = await engine.process(make_envelope())

        self.assertEqual(
            ["a-start", "a-end", "b-start", "b-end", "c-start", "c-end"],
            sequence,
        )
        self.assertTrue(result.success)
        self.assertEqual(3, result.delivered_handler_count)

    async def test_duplicate_handler_registration_preserves_two_entries(self) -> None:
        engine = EventEngine()
        calls: list[str] = []

        async def handler(envelope: EventEnvelope) -> None:
            calls.append("handler")

        engine.register("test.occurred", handler)
        engine.register("test.occurred", handler)

        result = await engine.process(make_envelope())

        self.assertEqual(["handler", "handler"], calls)
        self.assertEqual(EventDeliveryResult(True, 2, None, None), result)

    async def test_same_envelope_has_two_independent_explicit_invocations(self) -> None:
        engine = EventEngine()
        envelope = make_envelope()
        received: list[EventEnvelope] = []

        async def handler(candidate: EventEnvelope) -> None:
            received.append(candidate)

        engine.register(envelope.event_name, handler)

        first_result = await engine.process(envelope)
        second_result = await engine.process(envelope)

        self.assertEqual([envelope, envelope], received)
        self.assertEqual(EventDeliveryResult(True, 1, None, None), first_result)
        self.assertEqual(EventDeliveryResult(True, 1, None, None), second_result)

    async def test_handler_failure_stops_remaining_and_preserves_count(self) -> None:
        engine = EventEngine()
        sequence: list[str] = []

        async def completed(envelope: EventEnvelope) -> None:
            sequence.append("completed")

        async def failing(envelope: EventEnvelope) -> None:
            sequence.append("failing")
            raise RuntimeError("bounded failure")

        async def remaining(envelope: EventEnvelope) -> None:
            sequence.append("remaining")

        for handler in (completed, failing, remaining):
            engine.register("test.occurred", handler)

        result = await engine.process(make_envelope())

        self.assertEqual(["completed", "failing"], sequence)
        self.assertFalse(result.success)
        self.assertEqual(1, result.delivered_handler_count)
        self.assertIs(
            EventDeliveryFailureCode.HANDLER_FAILURE,
            result.failure_code,
        )
        self.assertEqual("bounded failure", result.failure_reason)

    async def test_later_explicit_invocation_remains_usable_after_handler_failure(self) -> None:
        engine = EventEngine()
        sequence: list[str] = []
        should_fail = True

        async def completed(envelope: EventEnvelope) -> None:
            sequence.append("completed")

        async def conditional(envelope: EventEnvelope) -> None:
            nonlocal should_fail
            sequence.append("conditional")
            if should_fail:
                should_fail = False
                raise RuntimeError("first invocation only")

        async def remaining(envelope: EventEnvelope) -> None:
            sequence.append("remaining")

        for handler in (completed, conditional, remaining):
            engine.register("test.occurred", handler)

        failed = await engine.process(make_envelope())
        self.assertEqual(["completed", "conditional"], sequence)
        self.assertEqual(1, failed.delivered_handler_count)
        self.assertIs(EventDeliveryFailureCode.HANDLER_FAILURE, failed.failure_code)

        sequence.clear()
        recovered = await engine.process(make_envelope())

        self.assertEqual(["completed", "conditional", "remaining"], sequence)
        self.assertEqual(EventDeliveryResult(True, 3, None, None), recovered)

    async def test_handler_failure_reason_is_bounded_and_has_no_traceback(self) -> None:
        engine = EventEngine()

        async def failing(envelope: EventEnvelope) -> None:
            raise RuntimeError("x" * 400)

        engine.register("test.occurred", failing)
        result = await engine.process(make_envelope())

        self.assertEqual(256, len(result.failure_reason or ""))
        self.assertNotIn("Traceback", result.failure_reason or "")

    async def test_registration_during_dispatch_uses_defensive_snapshot(self) -> None:
        engine = EventEngine()
        sequence: list[str] = []

        async def later(envelope: EventEnvelope) -> None:
            sequence.append("later")

        async def registering(envelope: EventEnvelope) -> None:
            sequence.append("registering")
            engine.register(envelope.event_name, later)

        engine.register("test.occurred", registering)

        first_result = await engine.process(make_envelope())
        self.assertEqual(["registering"], sequence)
        self.assertEqual(1, first_result.delivered_handler_count)

        sequence.clear()
        second_result = await engine.process(make_envelope())
        self.assertEqual(["registering", "later"], sequence)
        self.assertEqual(2, second_result.delivered_handler_count)

    async def test_process_does_not_mutate_envelope_or_domain_event(self) -> None:
        engine = EventEngine()
        envelope = make_envelope()
        event = envelope.event
        before = (hash(envelope), hash(event), envelope.event_name, event.event_name)

        async def handler(received: EventEnvelope) -> None:
            self.assertIs(envelope, received)
            self.assertIs(event, received.event)

        engine.register(envelope.event_name, handler)
        await engine.process(envelope)

        self.assertEqual(
            before,
            (hash(envelope), hash(event), envelope.event_name, event.event_name),
        )

    def test_result_is_frozen_and_failure_codes_are_exact(self) -> None:
        result = EventDeliveryResult(True, 1, None, None)

        with self.assertRaises((AttributeError, TypeError)):
            result.success = False  # type: ignore[misc]

        failure_codes = {code.value for code in EventDeliveryFailureCode}
        self.assertEqual(
            {
                "invalid_envelope",
                "no_handler",
                "handler_failure",
            },
            failure_codes,
        )
        self.assertNotIn("registration_error", failure_codes)
        self.assertTrue(issubclass(EventEngineRegistrationError, ValueError))

    def test_registration_rejects_invalid_boundary_values(self) -> None:
        engine = EventEngine()

        with self.assertRaises(EventEngineRegistrationError):
            engine.register(1, lambda envelope: None)  # type: ignore[arg-type]
        with self.assertRaises(EventEngineRegistrationError):
            engine.register(" ", lambda envelope: None)  # type: ignore[arg-type]
        with self.assertRaises(EventEngineRegistrationError):
            engine.register("test.occurred", object())  # type: ignore[arg-type]

    def test_source_has_no_parallel_retry_persistence_or_broker_constructs(self) -> None:
        source_path = Path("core/event/event_engine.py")
        source = source_path.read_text(encoding="utf-8")
        normalized_source = source.lower()
        tree = ast.parse(source)
        imports = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        } | {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }

        self.assertIn("core.domain.event_envelope", imports)
        self.assertFalse(any(name.startswith("core.event") for name in imports))
        for prohibited in (
            "asyncio.gather",
            "create_task",
            "taskgroup",
            "worker pool",
            "fan-out",
            "retry",
            "backoff",
            "max_retry",
            "dedupe",
            "deduplication",
            "idempotency",
            "processed_event",
            "event_id_cache",
            "ledger",
            "psycopg",
            "postgres",
            "registry",
            "event_store",
            "event log",
            "outbox",
            "inbox",
            "filesystem queue",
            "redis",
            "kafka",
            "rabbitmq",
            "nats",
            "celery",
            "http",
            "websocket",
            "datetime.utcnow",
        ):
            self.assertNotIn(prohibited, normalized_source)


if __name__ == "__main__":
    unittest.main()
