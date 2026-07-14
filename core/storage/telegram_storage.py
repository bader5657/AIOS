from pathlib import Path
from tempfile import NamedTemporaryFile

from telegram import Message
from telegram.ext import ContextTypes

from core.app.input_classifier import InputType, classify_telegram_message
from core.storage.file_storage import save_file


async def save_telegram_attachment(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> str | None:
    input_type = classify_telegram_message(message)

    telegram_file = None
    suffix = ""

    if input_type == InputType.IMAGE and message.photo:
        telegram_file = await context.bot.get_file(message.photo[-1].file_id)
        suffix = ".jpg"

    elif input_type == InputType.VOICE and message.voice:
        telegram_file = await context.bot.get_file(message.voice.file_id)
        suffix = ".ogg"

    elif input_type == InputType.DOCUMENT and message.document:
        telegram_file = await context.bot.get_file(message.document.file_id)
        suffix = Path(message.document.file_name or "").suffix

    elif input_type == InputType.VIDEO and message.video:
        telegram_file = await context.bot.get_file(message.video.file_id)
        suffix = ".mp4"

    elif input_type == InputType.AUDIO and message.audio:
        telegram_file = await context.bot.get_file(message.audio.file_id)
        suffix = Path(message.audio.file_name or "").suffix or ".mp3"

    if telegram_file is None:
        return None

    with NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_path = temporary_file.name

    try:
        await telegram_file.download_to_drive(temporary_path)
        return save_file(temporary_path)
    finally:
        Path(temporary_path).unlink(missing_ok=True)
