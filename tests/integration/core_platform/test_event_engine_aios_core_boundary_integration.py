import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from core.aios_core import (
    AIOSCore,
    CoreRouteFailureCode,
    CoreRouteResult,
    CoreRouteTarget,
)
from core.app.input_classifier import InputType
from core.domain.domain_event import DomainEvent
from core.event import EventDeliveryFailureCode, EventDeliveryResult, EventEngine
from core.ingestion import universal_ingestion
from core.pipeline.asset_pipeline import AssetPipelineResult


class ApprovedDomainEvent(DomainEvent):
    def __init__(self) -> None:
        super().__init__(
            "stage-8-1-4-event",
            datetime(2026, 8, 20, 2, 30, tzinfo=timezone.utc),
            "document.registered",
        )


def telegram_document_message():
    return SimpleNamespace(
        photo=None,
        voice=None,
        document=SimpleNamespace(file_name="exact.bin"),
        video=None,
        audio=None,
        text=None,
        caption=None,
        from_user=SimpleNamespace(id=7, username="owner"),
        chat=SimpleNamespace(id=8),
        message_id=9,
    )


class EventEngineAIOSCoreBoundaryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pipeline_result = AssetPipelineResult(
            success=True,
            stored_path="/stored/original.bin",
            metadata={"media_type": "document", "exact": True},
            manifest_path="/manifests/exact.json",
            register_handoff_ready=True,
        )
        self.registry = SimpleNamespace(
            register=AsyncMock(return_value=SimpleNamespace(record_id=814))
        )
        self.event = ApprovedDomainEvent()
        patches = (
            patch.object(
                universal_ingestion,
                "run_asset_pipeline",
                AsyncMock(return_value=self.pipeline_result),
            ),
            patch.object(
                universal_ingestion,
                "recognize_telegram_message",
                return_value=InputType.DOCUMENT,
            ),
            patch.object(
                universal_ingestion,
                "classify_telegram_message",
                return_value=InputType.DOCUMENT,
            ),
        )
        for active_patch in patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)

    async def ingest(self, **kwargs):
        return await universal_ingestion.ingest_telegram_message(
            telegram_document_message(),
            SimpleNamespace(),
            registry=self.registry,
            **kwargs,
        )

    @staticmethod
    def successful_engine():
        engine = EventEngine()
        seen = []

        async def handler(envelope):
            seen.append(envelope)

        engine.register("document.registered", handler)
        engine.process = AsyncMock(wraps=engine.process)
        return engine, seen

    async def test_success_hands_same_unchanged_envelope_to_real_core_once(self):
        engine, handler_seen = self.successful_engine()
        core = SimpleNamespace(route=AsyncMock(wraps=AIOSCore().route))
        event_state = (self.event.id, self.event.event_name, self.event.occurred_at)

        result = await self.ingest(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=14,
            aios_core=core,
        )

        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        engine_envelope = engine.process.await_args.args[0]
        core_envelope = core.route.await_args.args[0]
        self.assertIs(engine_envelope, core_envelope)
        self.assertIs(handler_seen[0], core_envelope)
        self.assertEqual(len(core.route.await_args.args), 1)
        self.assertIs(core_envelope.event, self.event)
        self.assertEqual(core_envelope.schema_version, 14)
        self.assertEqual(
            (self.event.id, self.event.event_name, self.event.occurred_at), event_state
        )
        self.assertTrue(result.event_delivery_succeeded)
        self.assertTrue(result.route_handoff_ready)

    async def test_no_domain_event_calls_neither_engine_nor_core(self):
        engine = SimpleNamespace(process=AsyncMock())
        core = SimpleNamespace(route=AsyncMock())

        result = await self.ingest(event_engine=engine, aios_core=core)

        engine.process.assert_not_awaited()
        core.route.assert_not_awaited()
        self.assertTrue(result.registration_succeeded)
        self.assertFalse(result.route_handoff_ready)

    async def test_each_bounded_event_failure_calls_no_core(self):
        for failure_code in EventDeliveryFailureCode:
            with self.subTest(failure_code=failure_code):
                engine = SimpleNamespace(
                    process=AsyncMock(
                        return_value=EventDeliveryResult(
                            False, 0, failure_code, "bounded event failure"
                        )
                    )
                )
                core = SimpleNamespace(route=AsyncMock())

                result = await self.ingest(
                    domain_event=self.event,
                    event_engine=engine,
                    event_schema_version=1,
                    aios_core=core,
                )

                engine.process.assert_awaited_once()
                core.route.assert_not_awaited()
                self.assertIs(result.event_delivery_failure_code, failure_code)
                self.assertFalse(result.route_handoff_ready)

    async def test_real_no_handler_and_handler_failure_never_reach_core(self):
        for handler_failure in (False, True):
            with self.subTest(handler_failure=handler_failure):
                engine = EventEngine()
                if handler_failure:
                    async def failing_handler(_envelope):
                        raise RuntimeError("bounded handler failure")

                    engine.register(self.event.event_name, failing_handler)
                engine.process = AsyncMock(wraps=engine.process)
                core = SimpleNamespace(route=AsyncMock())

                result = await self.ingest(
                    domain_event=self.event,
                    event_engine=engine,
                    event_schema_version=2,
                    aios_core=core,
                )

                engine.process.assert_awaited_once()
                core.route.assert_not_awaited()
                expected = (
                    EventDeliveryFailureCode.HANDLER_FAILURE
                    if handler_failure
                    else EventDeliveryFailureCode.NO_HANDLER
                )
                self.assertIs(result.event_delivery_failure_code, expected)
                self.assertFalse(result.route_handoff_ready)

    async def test_core_bounded_non_success_is_projection_only(self):
        engine, _ = self.successful_engine()
        core_result = CoreRouteResult(
            success=False,
            route_target=None,
            failure_code=CoreRouteFailureCode.INVALID_INPUT,
            failure_reason="injected projection evidence only",
        )
        core = SimpleNamespace(route=AsyncMock(return_value=core_result))

        result = await self.ingest(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=3,
            aios_core=core,
        )

        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        self.assertTrue(result.event_delivery_succeeded)
        self.assertFalse(result.route_handoff_ready)
        self.assertTrue(result.registration_succeeded)

    async def test_success_with_wrong_route_target_is_not_ready(self):
        engine, _ = self.successful_engine()
        core = SimpleNamespace(
            route=AsyncMock(
                return_value=CoreRouteResult(True, None, None, None)
            )
        )

        result = await self.ingest(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=4,
            aios_core=core,
        )

        self.assertFalse(result.route_handoff_ready)
        core.route.assert_awaited_once()

    async def test_missing_core_after_delivery_success_is_explicit_error(self):
        engine, _ = self.successful_engine()

        with self.assertRaisesRegex(
            ValueError, "aios_core is required after successful event delivery"
        ):
            await self.ingest(
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=5,
            )

        engine.process.assert_awaited_once()
        self.registry.register.assert_awaited_once()

    async def test_unexpected_engine_exception_propagates_before_core(self):
        engine = SimpleNamespace(
            process=AsyncMock(side_effect=RuntimeError("unexpected engine defect"))
        )
        core = SimpleNamespace(route=AsyncMock())

        with self.assertRaisesRegex(RuntimeError, "unexpected engine defect"):
            await self.ingest(
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=6,
                aios_core=core,
            )

        engine.process.assert_awaited_once()
        core.route.assert_not_awaited()
        self.registry.register.assert_awaited_once()

    async def test_unexpected_core_exception_propagates_without_retry(self):
        engine, _ = self.successful_engine()
        core = SimpleNamespace(
            route=AsyncMock(side_effect=RuntimeError("unexpected core defect"))
        )

        with self.assertRaisesRegex(RuntimeError, "unexpected core defect"):
            await self.ingest(
                domain_event=self.event,
                event_engine=engine,
                event_schema_version=7,
                aios_core=core,
            )

        engine.process.assert_awaited_once()
        core.route.assert_awaited_once()
        self.registry.register.assert_awaited_once()

    async def test_only_brain_boundary_target_can_set_readiness(self):
        engine, _ = self.successful_engine()
        core = SimpleNamespace(
            route=AsyncMock(
                return_value=CoreRouteResult(
                    True, CoreRouteTarget.AIOS_BRAIN_BOUNDARY, None, None
                )
            )
        )

        result = await self.ingest(
            domain_event=self.event,
            event_engine=engine,
            event_schema_version=8,
            aios_core=core,
        )

        self.assertTrue(result.route_handoff_ready)
        core.route.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
