"""Contract tests for the fresh AIOS Core runtime."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
import inspect
from pathlib import Path
import unittest

import core.aios_core as aios_core_module
from core.aios_core import (
    AIOSCore,
    CoreRouteFailureCode,
    CoreRouteResult,
    CoreRouteTarget,
)
from core.domain.domain_event import DomainEvent
from core.domain.event_envelope import EventEnvelope


class SampleEvent(DomainEvent):
    __slots__ = ("_payload",)

    def __init__(
        self,
        event_id: str,
        event_name: str,
        payload: object,
    ) -> None:
        super().__init__(
            event_id,
            datetime(2026, 8, 19, 9, 0, tzinfo=timezone.utc),
            event_name,
        )
        self._payload = payload

    @property
    def payload(self) -> object:
        return self._payload


def make_envelope(
    event_id: str = "event-1",
    event_name: str = "unknown.occurred",
    payload: object = None,
) -> EventEnvelope:
    return EventEnvelope(
        SampleEvent(event_id, event_name, payload),
        aggregate_id="aggregate-1",
        correlation_id="correlation-1",
        causation_id="causation-1",
        schema_version=1,
    )


class AIOSCoreTests(unittest.IsolatedAsyncioTestCase):
    def test_construction_is_stateless_and_route_is_only_public_operation(self) -> None:
        core = AIOSCore()

        self.assertFalse(hasattr(core, "__dict__"))
        self.assertEqual(
            {"route"},
            {name for name in vars(AIOSCore) if not name.startswith("_")},
        )
        self.assertFalse(hasattr(core, "process"))
        self.assertFalse(hasattr(core, "dispatch"))
        self.assertFalse(hasattr(core, "execute"))
        self.assertFalse(hasattr(core, "reason"))
        self.assertFalse(hasattr(core, "invoke_brain"))
        self.assertFalse(hasattr(core, "route_to_specialist"))

    def test_route_is_async(self) -> None:
        self.assertTrue(inspect.iscoroutinefunction(AIOSCore.route))

    async def test_valid_envelope_returns_exact_success(self) -> None:
        result = await AIOSCore().route(make_envelope())

        self.assertEqual(
            CoreRouteResult(
                success=True,
                route_target=CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
                failure_code=None,
                failure_reason=None,
            ),
            result,
        )
        self.assertIs(CoreRouteTarget.AIOS_BRAIN_BOUNDARY, result.route_target)
        self.assertIsNone(result.failure_code)
        self.assertIsNone(result.failure_reason)

    async def test_invalid_input_returns_exact_bounded_failure(self) -> None:
        for candidate in (None, object(), "event", 1):
            with self.subTest(candidate=candidate):
                result = await AIOSCore().route(candidate)  # type: ignore[arg-type]

                self.assertEqual(
                    CoreRouteResult(
                        success=False,
                        route_target=None,
                        failure_code=CoreRouteFailureCode.INVALID_INPUT,
                        failure_reason="route input must be an EventEnvelope",
                    ),
                    result,
                )
                self.assertIsNone(result.route_target)
                self.assertIs(
                    CoreRouteFailureCode.INVALID_INPUT,
                    result.failure_code,
                )

    async def test_repeated_calls_are_equal_and_independent(self) -> None:
        core = AIOSCore()
        envelope = make_envelope()

        first = await core.route(envelope)
        invalid = await core.route(object())  # type: ignore[arg-type]
        second = await core.route(envelope)

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertFalse(invalid.success)
        self.assertFalse(hasattr(core, "__dict__"))

    async def test_all_event_names_route_to_the_same_sole_target(self) -> None:
        first = make_envelope("event-1", "customer.created")
        second = make_envelope("event-2", "unlisted.event")

        first_result = await AIOSCore().route(first)
        second_result = await AIOSCore().route(second)

        self.assertEqual(first_result, second_result)
        self.assertIs(
            CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
            first_result.route_target,
        )

    async def test_payload_does_not_affect_routing(self) -> None:
        opaque_payload = object()
        first = make_envelope("event-1", payload=opaque_payload)
        second = make_envelope(
            "event-2",
            payload={"intent": "finance", "content": ["order", "product"]},
        )

        self.assertEqual(
            await AIOSCore().route(first),
            await AIOSCore().route(second),
        )
        self.assertIs(opaque_payload, first.event.payload)

    async def test_envelope_and_domain_event_remain_unchanged(self) -> None:
        payload = object()
        envelope = make_envelope(payload=payload)
        event = envelope.event
        envelope_snapshot = (
            envelope.event,
            envelope.aggregate_id,
            envelope.correlation_id,
            envelope.causation_id,
            envelope.schema_version,
        )
        event_snapshot = (event.id, event.occurred_at, event.event_name, event.payload)

        await AIOSCore().route(envelope)

        self.assertEqual(envelope_snapshot, (
            envelope.event,
            envelope.aggregate_id,
            envelope.correlation_id,
            envelope.causation_id,
            envelope.schema_version,
        ))
        self.assertEqual(
            event_snapshot,
            (event.id, event.occurred_at, event.event_name, event.payload),
        )
        self.assertIs(event, envelope.event)
        self.assertIs(payload, event.payload)

    def test_result_is_frozen_slotted_and_has_exactly_four_fields(self) -> None:
        result = CoreRouteResult(True, CoreRouteTarget.AIOS_BRAIN_BOUNDARY, None, None)

        self.assertEqual(
            ("success", "route_target", "failure_code", "failure_reason"),
            tuple(field.name for field in fields(CoreRouteResult)),
        )
        self.assertFalse(hasattr(result, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            result.success = False  # type: ignore[misc]

    def test_exactly_one_target_and_one_failure_code_exist(self) -> None:
        self.assertEqual(
            [("AIOS_BRAIN_BOUNDARY", "aios_brain_boundary")],
            [(member.name, member.value) for member in CoreRouteTarget],
        )
        self.assertEqual(
            [("INVALID_INPUT", "invalid_input")],
            [(member.name, member.value) for member in CoreRouteFailureCode],
        )

    def test_package_exports_only_approved_symbols(self) -> None:
        self.assertEqual(
            {
                "AIOSCore",
                "CoreRouteFailureCode",
                "CoreRouteResult",
                "CoreRouteTarget",
            },
            set(aios_core_module.__all__),
        )

    def test_runtime_has_only_approved_dependencies_and_behavior(self) -> None:
        runtime_path = Path(__file__).parents[3] / "core" / "aios_core" / "core.py"
        tree = ast.parse(runtime_path.read_text(encoding="utf-8"))
        imports = {
            node.module or alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }

        self.assertEqual(
            {"__future__", "dataclasses", "enum", "core.domain.event_envelope"},
            imports,
        )
        self.assertFalse(
            calls
            & {
                "create_task",
                "gather",
                "sleep",
                "open",
                "connect",
                "request",
                "retry",
            }
        )
        self.assertFalse(
            attributes
            & {
                "event",
                "event_name",
                "payload",
                "history",
                "session",
                "cache",
            }
        )

    def test_historical_runtime_files_are_absent(self) -> None:
        package_path = Path(__file__).parents[3] / "core" / "aios_core"

        self.assertEqual(
            {"__init__.py", "core.py"},
            {path.name for path in package_path.iterdir() if path.suffix == ".py"},
        )


if __name__ == "__main__":
    unittest.main()
