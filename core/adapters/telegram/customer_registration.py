"""Thin opt-in Telegram transport for the customer application."""
import asyncio
import os

from core.app.customer_registration import Actor, CustomerRegistration

def configured_registration():
    if os.environ.get("AIOS_CUSTOMER_REGISTRATION_ENABLED") != "1":
        return None
    from core.adapters.postgres_customer_registration import PostgresCustomerRegistrationTransactions
    dsn = os.environ.get("AIOS_CUSTOMER_REGISTRATION_DATABASE_URL")
    return CustomerRegistration(PostgresCustomerRegistrationTransactions(dsn))

async def handle_customer_registration(update, registration):
    edited = getattr(update, "edited_message", None)
    message = update.message or edited
    if message is None or (edited is None and type(message.text) is not str):
        return False
    command = (message.text or "").partition(" ")[0]
    if edited is None and command not in ("catat_pelanggan", "konfirmasi_pelanggan"):
        return False
    # Business messages never fall through to the generic ingestion/storage path.
    if registration is None:
        await message.reply_text("Fungsi pelanggan belum diaktifkan.")
        return True
    user, chat = update.effective_user, update.effective_chat
    if (user is None or chat is None or getattr(message, "forward_origin", None)
            or getattr(message, "sender_chat", None) or getattr(message, "via_bot", None)):
        await message.reply_text("Akses ditolak.")
        return True
    actor = Actor(user.id, chat.id, chat.type, user.is_bot)
    try:
        if edited is not None:
            reply = await asyncio.to_thread(registration.invalidate_edit, actor, message.message_id)
        else:
            reply = await asyncio.to_thread(registration.handle, actor, message.message_id, message.text)
    except Exception:
        # Do not disclose database addresses, customer data, or bearer tokens.
        reply = "Permintaan belum dapat dipastikan. Ulangi pesan konfirmasi yang sama."
    await message.reply_text(reply, parse_mode=None)
    return True
