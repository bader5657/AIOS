import json
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

from core.app.request_context import RequestContext
from core.ingestion.universal_ingestion import ingest_telegram_message
from core.mission.status import mission_status

load_dotenv("/opt/aios/runtime/config/runtime.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN belum diisi di runtime.env")


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

    request_context = RequestContext.from_telegram(
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        username=update.effective_user.username or "",
        text=ingestion.text,
    )

    output = request_context.to_dict()
    output["input_type"] = ingestion.input_type.value
    output["stored_path"] = ingestion.stored_path
    output["manifest_path"] = ingestion.manifest_path
    output["metadata"] = ingestion.metadata

    print(json.dumps(output, ensure_ascii=False, indent=2))

    response = (
        "🤖 AIOS menerima input.\n\n"
        f"Jenis : {ingestion.input_type.value}\n"
        f"Request : {request_context.message_id}"
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
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(~filters.COMMAND, handle_update))

    print("AIOS Telegram Adapter Online...")

    app.run_polling()


if __name__ == "__main__":
    main()
