import unittest
from unittest.mock import Mock
from test_telegram_customer_registration import update
from core.adapters.telegram.customer_registration import handle_customer_registration

class TelegramCustomerFormTests(unittest.IsolatedAsyncioTestCase):
    async def test_form_start_cancel_and_invalid_form_terminate_business_route(self):
        for text in ("catat pelanggan", "batal pelanggan", "Nama: Ani\nUnknown: bad"):
            event = update(text)
            service = Mock()
            service.handle.return_value = "business reply"
            self.assertTrue(await handle_customer_registration(event, service))
            self.assertEqual(service.handle.call_args.args[2], text)

    async def test_disabled_form_stays_closed(self):
        event = update("Nama: Ani\nAlamat: Jalan Uji 123\nKota: Solo")
        self.assertTrue(await handle_customer_registration(event, None))
        self.assertIn("belum diaktifkan", event.message.reply_text.call_args.args[0])

    async def test_preview_confirmation_is_copyable_as_separate_message(self):
        event = update("Nama: Ani")
        service = Mock()
        command = "konfirmasi_pelanggan " + "a"*64
        service.handle.return_value = "Preview\nKirim: " + command
        await handle_customer_registration(event, service)
        self.assertEqual(event.message.reply_text.await_count, 2)
        self.assertEqual(event.message.reply_text.await_args_list[-1].args, (command,))
        self.assertIsNone(event.message.reply_text.await_args_list[-1].kwargs["parse_mode"])

    async def test_forwarded_form_never_reaches_authorization_service(self):
        event = update("Nama: Ani")
        event.message.forward_origin = object()
        service = Mock()
        self.assertTrue(await handle_customer_registration(event, service))
        service.handle.assert_not_called()
