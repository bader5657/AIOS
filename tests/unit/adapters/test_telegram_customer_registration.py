import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
from core.adapters.telegram.customer_registration import handle_customer_registration, configured_registration

def update(text="catat_pelanggan {}", **changes):
    message = SimpleNamespace(text=text, message_id=10, forward_origin=None,
                              sender_chat=None, via_bot=None, reply_text=AsyncMock())
    result = SimpleNamespace(message=message, edited_message=None,
        effective_user=SimpleNamespace(id=42, is_bot=False),
        effective_chat=SimpleNamespace(id=42, type="private"))
    for key, value in changes.items():
        setattr(result, key, value)
    return result

class TelegramCustomerRegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_disabled_does_not_fall_through_or_open_database(self):
        event = update()
        self.assertTrue(await handle_customer_registration(event, None))
        self.assertIn("belum diaktifkan", event.message.reply_text.call_args.args[0])

    async def test_transport_passes_numeric_identity_and_exact_text(self):
        event = update('catat_pelanggan {"notes":"  x  "}')
        service = Mock()
        service.handle.return_value = "committed"
        self.assertTrue(await handle_customer_registration(event, service))
        actor, message_id, text = service.handle.call_args.args
        self.assertEqual((actor.user_id, actor.chat_id, actor.chat_type), (42,42,"private"))
        self.assertEqual((message_id, text), (10,event.message.text))
        event.message.reply_text.assert_awaited_once_with("committed", parse_mode=None)

    async def test_forwarded_and_anonymous_sender_never_reach_service(self):
        for field in ("forward_origin", "sender_chat", "via_bot"):
            event = update()
            setattr(event.message, field, object())
            service = Mock()
            await handle_customer_registration(event, service)
            service.handle.assert_not_called()

    async def test_failure_does_not_claim_success_or_leak_secret(self):
        event = update("konfirmasi_pelanggan token")
        service = Mock()
        service.handle.side_effect = RuntimeError("postgres://secret")
        await handle_customer_registration(event, service)
        reply = event.message.reply_text.call_args.args[0]
        self.assertNotIn("secret", reply)
        self.assertNotIn("tersimpan", reply)

    async def test_edit_routes_to_invalidation_even_when_command_removed(self):
        event = update("now ordinary text")
        event.edited_message, event.message = event.message, None
        service = Mock()
        service.invalidate_edit.return_value = "invalidated"
        await handle_customer_registration(event, service)
        service.invalidate_edit.assert_called_once()
        service.handle.assert_not_called()

    async def test_unrelated_text_preserves_ingestion_path(self):
        service = Mock()
        self.assertFalse(await handle_customer_registration(update("status"), service))
        service.handle.assert_not_called()

    def test_configuration_defaults_disabled(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(configured_registration())
