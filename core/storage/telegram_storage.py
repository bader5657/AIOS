from pathlib import Path
from tempfile import NamedTemporaryFile

from telegram import Message
from telegram.ext import ContextTypes

from core.app.input_classifier import InputType, recognize_telegram_message
from core.storage.file_storage import save_file


async def save_telegram_attachment(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    input_type: InputType | None = None,
) -> str | None:
    input_type = input_type or recognize_telegram_message(message)

    telegram_file = None
    original_filename = None
    suffix = ""

    if input_type == InputType.IMAGE and message.photo:
        telegram_file = await context.bot.get_file(message.photo[-1].file_id)
        suffix = ".jpg"

    elif input_type == InputType.VOICE and message.voice:
        telegram_file = await context.bot.get_file(message.voice.file_id)
        suffix = ".ogg"

    elif input_type == InputType.DOCUMENT and message.document:
        telegram_file = await context.bot.get_file(message.document.file_id)
        original_filename = message.document.file_name
        suffix = Path(original_filename or "").suffix

    elif input_type in (InputType.PDF, InputType.DOC, InputType.SPREADSHEET):
        telegram_file = await context.bot.get_file(message.document.file_id)
        original_filename = message.document.file_name
        suffix = Path(original_filename or "").suffix

    elif input_type == InputType.VIDEO and message.video:
        telegram_file = await context.bot.get_file(message.video.file_id)
        original_filename = getattr(message.video, "file_name", None)
        suffix = Path(original_filename or "").suffix or ".mp4"

    elif input_type == InputType.AUDIO and message.audio:
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
            storage_class=input_type.value,
            original_filename=original_filename,
        )
    except OSError:
        return None
    finally:
        Path(temporary_path).unlink(missing_ok=True)
