import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from core.ingestion.universal_ingestion import ingest_telegram_message
from core.mission.status import mission_status

load_dotenv("/opt/aios/runtime/config/runtime.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    await update.message.reply_text(
        "🤖 AIOS Online\n\n"
        "Version : 0.1.0-alpha\n"
        "Status  : Healthy"
    )


async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (
        update.message is None
        or update.effective_user is None
        or update.effective_chat is None
    ):
        return

    text = (update.message.text or "").strip().lower()

    # ===== Mission Control =====
    if text == "status":
        await update.message.reply_text(mission_status())
        return

    ingestion = await ingest_telegram_message(update.message, context)

    if not ingestion.register_handoff_ready:
        return

    response = (
        "🤖 AIOS menerima input.\n\n"
        f"Jenis : {ingestion.input_type.value}\n"
        f"Request : {update.message.message_id}"
    )

    if ingestion.stored_path:
        response += f"\n\nDisimpan:\n{ingestion.stored_path}"

    if ingestion.manifest_path:
        response += f"\n\nManifest:\n{ingestion.manifest_path}"

    if ingestion.metadata:
        response += (
            f"\n\nMime : {ingestion.metadata.get('mime_type')}"
            f"\nUkuran : {ingestion.metadata.get('file_size_bytes')} byte"
        )

        if "width" in ingestion.metadata:
            response += (
                f"\nResolusi : "
                f"{ingestion.metadata['width']} x "
                f"{ingestion.metadata['height']}"
            )

    await update.message.reply_text(response)


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN belum diisi di runtime.env")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(~filters.COMMAND, handle_update))

    print("AIOS Telegram Adapter Online...")

    app.run_polling()


if __name__ == "__main__":
    main()
