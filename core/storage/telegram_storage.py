from pathlib import Path
from tempfile import NamedTemporaryFile

from telegram import Message
from telegram.ext import ContextTypes

from core.storage.file_storage import save_file


async def save_telegram_attachment(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    media_type: str,
) -> str | None:
    telegram_file = None
    original_filename = None
    suffix = ""

    if media_type == "image" and message.photo:
        telegram_file = await context.bot.get_file(message.photo[-1].file_id)
        suffix = ".jpg"

    elif media_type == "voice" and message.voice:
        telegram_file = await context.bot.get_file(message.voice.file_id)
        suffix = ".ogg"

    elif media_type == "document" and message.document:
        telegram_file = await context.bot.get_file(message.document.file_id)
        original_filename = message.document.file_name
        suffix = Path(original_filename or "").suffix

    elif media_type in ("pdf", "doc", "spreadsheet"):
        telegram_file = await context.bot.get_file(message.document.file_id)
        original_filename = message.document.file_name
        suffix = Path(original_filename or "").suffix

    elif media_type == "video" and message.video:
        telegram_file = await context.bot.get_file(message.video.file_id)
        original_filename = getattr(message.video, "file_name", None)
        suffix = Path(original_filename or "").suffix or ".mp4"

    elif media_type == "audio" and message.audio:
        telegram_file = await context.bot.get_file(message.audio.file_id)
        original_filename = message.audio.file_name
        suffix = Path(original_filename or "").suffix or ".mp3"

    if telegram_file is None:
        return None

    with NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_path = temporary_file.name

    try:
        await telegram_file.download_to_drive(temporary_path)
        return save_file(
            temporary_path,
            storage_class=media_type,
            original_filename=original_filename,
        )
    except OSError:
        return None
    finally:
        Path(temporary_path).unlink(missing_ok=True)
