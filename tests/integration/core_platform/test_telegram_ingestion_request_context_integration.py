import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from core.adapters.telegram import main as telegram_adapter
from core.app.input_classifier import InputType
from core.ingestion import universal_ingestion
from core.pipeline.asset_pipeline import AssetPipelineResult


def fake_message(*, text="Original Mixed CASE text", username="operator"):
    return SimpleNamespace(
        photo=None,
        voice=None,
        document=None,
        video=None,
        audio=None,
        text=text,
        caption=None,
        from_user=SimpleNamespace(id=101, username=username),
        chat=SimpleNamespace(id=-202),
        message_id=303,
        media_group_id=None,
        reply_text=AsyncMock(),
    )


def fake_update(message):
    return SimpleNamespace(
        update_id=404,
        message=message,
        effective_user=None if message is None else message.from_user,
        effective_chat=None if message is None else message.chat,
    )


def ingestion_result(*, input_type=InputType.TEXT, ready=False):
    return universal_ingestion.IngestionResult(
        input_type=input_type,
        recognized_input_type=input_type,
        stored_path=None,
        manifest_path=None,
        metadata={},
        text="",
        register_handoff_ready=ready,
        process_handoff_ready=False,
        route_handoff_ready=False,
        respond_acknowledgement_ready=ready,
    )


class TelegramIngestionRequestContextIntegrationTests(
    unittest.IsolatedAsyncioTestCase
):
    async def test_original_message_reaches_ingestion_and_context_is_created_once(self):
        message = fake_message()
        update = fake_update(message)
        telegram_context = SimpleNamespace(bot=SimpleNamespace())
        pipeline = AssetPipelineResult(
            success=True,
            manifest_path=None,
            register_handoff_ready=True,
        )
        authoritative_factory = universal_ingestion.RequestContext.from_telegram

        with (
            patch.object(
                universal_ingestion,
                "run_asset_pipeline",
                AsyncMock(return_value=pipeline),
            ) as pipeline_call,
            patch.object(
                universal_ingestion.RequestContext,
                "from_telegram",
                wraps=authoritative_factory,
            ) as context_factory,
            patch.object(
                universal_ingestion.PostgresRegistry,
                "from_environment",
            ) as registry_factory,
            patch.object(
                telegram_adapter,
                "ingest_telegram_message",
                AsyncMock(side_effect=universal_ingestion.ingest_telegram_message),
            ) as ingestion_call,
        ):
            await telegram_adapter.handle_update(update, telegram_context)

        ingestion_call.assert_awaited_once_with(message, telegram_context)
        self.assertIs(ingestion_call.await_args.args[0], message)
        context_factory.assert_called_once_with(
            user_id=101,
            chat_id=-202,
            message_id=303,
            username="operator",
            text="Original Mixed CASE text",
        )
        pipeline_call.assert_awaited_once()
        self.assertIs(pipeline_call.await_args.kwargs["message"], message)
        self.assertEqual(
            pipeline_call.await_args.kwargs["text"],
            "Original Mixed CASE text",
        )
        self.assertEqual(
            pipeline_call.await_args.kwargs["request_context"].to_dict()[
                "username"
            ],
            "operator",
        )
        registry_factory.assert_not_called()
        message.reply_text.assert_awaited_once()
        self.assertIn("Request : 303", message.reply_text.await_args.args[0])

    async def test_username_fallback_and_link_recognition_remain_in_ingestion(self):
        cases = (
            ("https://example.com/Path?Q=Mixed", InputType.WEB_LINK),
            ("https://youtu.be/AbCdEf", InputType.YOUTUBE_LINK),
        )
        for original_text, expected_type in cases:
            with self.subTest(expected_type=expected_type):
                message = fake_message(text=original_text, username=None)
                pipeline = AssetPipelineResult(
                    success=True,
                    manifest_path=None,
                    register_handoff_ready=True,
                )
                authoritative_factory = (
                    universal_ingestion.RequestContext.from_telegram
                )
                with (
                    patch.object(
                        universal_ingestion,
                        "run_asset_pipeline",
                        AsyncMock(return_value=pipeline),
                    ) as pipeline_call,
                    patch.object(
                        universal_ingestion.RequestContext,
                        "from_telegram",
                        wraps=authoritative_factory,
                    ) as context_factory,
                    patch.object(
                        telegram_adapter,
                        "ingest_telegram_message",
                        AsyncMock(
                            side_effect=universal_ingestion.ingest_telegram_message
                        ),
                    ),
                ):
                    await telegram_adapter.handle_update(
                        fake_update(message),
                        SimpleNamespace(bot=SimpleNamespace()),
                    )

                context_factory.assert_called_once_with(
                    user_id=101,
                    chat_id=-202,
                    message_id=303,
                    username="",
                    text=original_text,
                )
                self.assertEqual(
                    pipeline_call.await_args.kwargs["recognized_input_type"],
                    expected_type.value,
                )
                self.assertEqual(
                    pipeline_call.await_args.kwargs["text"],
                    original_text,
                )

    async def test_malformed_updates_stop_before_ingestion(self):
        cases = (
            SimpleNamespace(
                message=None,
                effective_user=None,
                effective_chat=None,
            ),
            SimpleNamespace(
                message=fake_message(),
                effective_user=None,
                effective_chat=SimpleNamespace(id=-202),
            ),
            SimpleNamespace(
                message=fake_message(),
                effective_user=SimpleNamespace(id=101),
                effective_chat=None,
            ),
        )
        for update in cases:
            with self.subTest(update=update):
                with patch.object(
                    telegram_adapter,
                    "ingest_telegram_message",
                    AsyncMock(),
                ) as ingestion_call:
                    await telegram_adapter.handle_update(
                        update,
                        SimpleNamespace(bot=SimpleNamespace()),
                    )
                ingestion_call.assert_not_awaited()
                if update.message is not None:
                    update.message.reply_text.assert_not_awaited()

    async def test_bounded_non_success_results_do_not_acknowledge(self):
        cases = (
            ("unsupported", ingestion_result(input_type=InputType.UNKNOWN)),
            ("empty", ingestion_result()),
            ("download_failure", ingestion_result(input_type=InputType.DOCUMENT)),
        )
        for name, result in cases:
            with self.subTest(name=name):
                message = fake_message(text=None)
                with patch.object(
                    telegram_adapter,
                    "ingest_telegram_message",
                    AsyncMock(return_value=result),
                ) as ingestion_call:
                    await telegram_adapter.handle_update(
                        fake_update(message),
                        SimpleNamespace(bot=SimpleNamespace()),
                    )
                ingestion_call.assert_awaited_once()
                message.reply_text.assert_not_awaited()

    async def test_bounded_exception_is_not_retried_or_acknowledged(self):
        message = fake_message()
        failure = RuntimeError("bounded ingestion failure")
        with patch.object(
            telegram_adapter,
            "ingest_telegram_message",
            AsyncMock(side_effect=failure),
        ) as ingestion_call:
            with self.assertRaisesRegex(
                RuntimeError,
                "bounded ingestion failure",
            ):
                await telegram_adapter.handle_update(
                    fake_update(message),
                    SimpleNamespace(bot=SimpleNamespace()),
                )
        ingestion_call.assert_awaited_once()
        message.reply_text.assert_not_awaited()

    async def test_ready_result_acknowledges_exactly_once(self):
        message = fake_message()
        with patch.object(
            telegram_adapter,
            "ingest_telegram_message",
            AsyncMock(return_value=ingestion_result(ready=True)),
        ) as ingestion_call:
            await telegram_adapter.handle_update(
                fake_update(message),
                SimpleNamespace(bot=SimpleNamespace()),
            )
        ingestion_call.assert_awaited_once()
        message.reply_text.assert_awaited_once()

    async def test_status_and_start_remain_outside_general_ingestion(self):
        status_message = fake_message(text="  StAtUs ")
        with (
            patch.object(
                telegram_adapter,
                "ingest_telegram_message",
                AsyncMock(),
            ) as ingestion_call,
            patch.object(
                telegram_adapter,
                "mission_status",
                return_value="healthy",
            ),
        ):
            await telegram_adapter.handle_update(
                fake_update(status_message),
                SimpleNamespace(bot=SimpleNamespace()),
            )
        ingestion_call.assert_not_awaited()
        status_message.reply_text.assert_awaited_once_with("healthy")

        start_message = fake_message(text="/start")
        await telegram_adapter.start(
            fake_update(start_message),
            SimpleNamespace(bot=SimpleNamespace()),
        )
        start_message.reply_text.assert_awaited_once()
        ingestion_call.assert_not_awaited()

    def test_adapter_source_preserves_boundary_and_has_no_hidden_side_effects(self):
        source = inspect.getsource(telegram_adapter)
        self.assertNotIn("RequestContext", source)
        self.assertNotIn("classify_telegram_message", source)
        self.assertNotIn("recognize_telegram_message", source)
        self.assertNotIn("get_file(", source)
        self.assertNotIn("download_to_drive", source)
        self.assertNotIn("save_telegram_attachment", source)
        self.assertNotIn("media_group_id", source)
        self.assertNotIn("run_polling(", inspect.getsource(telegram_adapter.handle_update))
        self.assertNotIn("retry", source.lower())
        self.assertNotIn("webhook", source.lower())

    def test_dependency_direction_has_no_reverse_adapter_imports(self):
        repository_root = Path(__file__).resolve().parents[3]
        reverse_roots = (
            repository_root / "core/domain",
            repository_root / "core/registry",
            repository_root / "core/event",
            repository_root / "core/aios_core",
        )
        for root in reverse_roots:
            for python_file in root.rglob("*.py"):
                self.assertNotIn(
                    "core.adapters.telegram",
                    python_file.read_text(encoding="utf-8"),
                    str(python_file),
                )

    def test_missing_token_fails_only_at_production_startup(self):
        with (
            patch.object(telegram_adapter, "TOKEN", None),
            patch.object(telegram_adapter.Application, "builder") as builder,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "TELEGRAM_BOT_TOKEN",
            ):
                telegram_adapter.main()
        builder.assert_not_called()
