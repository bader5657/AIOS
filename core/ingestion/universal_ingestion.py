from dataclasses import dataclass
from pathlib import Path

from telegram import Message
from telegram.ext import ContextTypes

from core.app.input_classifier import (
    InputType,
    classify_telegram_message,
    recognize_telegram_message,
)
from core.app.request_context import RequestContext
from core.domain.domain_event import DomainEvent
from core.domain.event_envelope import EventEnvelope
from core.event import EventDeliveryFailureCode, EventEngine
from core.pipeline.asset_pipeline import run_asset_pipeline
from core.registry import (
    PostgresRegistry,
    RegistryPersistenceError,
    RegistryPersistenceInput,
)


@dataclass(slots=True)
class IngestionResult:
    input_type: InputType
    recognized_input_type: InputType
    stored_path: str | None
    manifest_path: str | None
    metadata: dict
    text: str
    register_handoff_ready: bool
    process_handoff_ready: bool
    route_handoff_ready: bool
    respond_acknowledgement_ready: bool
    registration_succeeded: bool = False
    registry_record_id: int | None = None
    event_publication_attempted: bool = False
    event_delivery_succeeded: bool = False
    event_delivery_failure_code: EventDeliveryFailureCode | None = None


def _file_original_types(message: Message) -> tuple[InputType, ...]:
    """Enumerate file originals in deterministic Telegram transport order."""
    originals = []
    if message.photo:
        originals.append(InputType.IMAGE)
    if message.voice:
        originals.append(InputType.VOICE)
    if message.document:
        filename = getattr(message.document, "file_name", None) or ""
        extension = Path(filename).suffix.removeprefix(".").lower()
        if extension == "pdf":
            originals.append(InputType.PDF)
        elif extension in ("doc", "docx"):
            originals.append(InputType.DOC)
        elif extension in ("xls", "xlsx", "csv", "ods"):
            originals.append(InputType.SPREADSHEET)
        else:
            originals.append(InputType.DOCUMENT)
    if message.video:
        originals.append(InputType.VIDEO)
    if message.audio:
        originals.append(InputType.AUDIO)
    return tuple(originals)


async def ingest_telegram_message(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    registry: PostgresRegistry | None = None,
    domain_event: DomainEvent | None = None,
    event_engine: EventEngine | None = None,
    event_schema_version: int | None = None,
) -> IngestionResult:
    recognized_input_type = recognize_telegram_message(message)
    input_type = classify_telegram_message(message)
    if input_type != InputType.TEXT:
        file_original_types = _file_original_types(message)
    else:
        file_original_types = ()
    text = message.text or message.caption or ""

    original_filename = None
    if message.document:
        original_filename = message.document.file_name
    elif message.audio:
        original_filename = getattr(message.audio, "file_name", None)
    elif message.video:
        original_filename = getattr(message.video, "file_name", None)

    if message.from_user is None or message.chat is None:
        raise ValueError("Telegram message identity is required for ingestion")

    request_context = RequestContext.from_telegram(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        message_id=message.message_id,
        username=getattr(message.from_user, "username", None) or "",
        text=text,
    )
    pipeline_result = await run_asset_pipeline(
        request_context=request_context,
        recognized_input_type=recognized_input_type.value,
        message=message,
        telegram_context=context,
        file_original_types=tuple(
            file_original_type.value for file_original_type in file_original_types
        ),
        original_filename=original_filename,
        text=text,
    )

    registration_succeeded = False
    registry_record_id = None
    event_publication_attempted = False
    event_delivery_succeeded = False
    event_delivery_failure_code = None
    manifest_path = pipeline_result.manifest_path
    if (
        pipeline_result.success
        and pipeline_result.register_handoff_ready
        and isinstance(manifest_path, str)
        and manifest_path
    ):
        persistence_input = RegistryPersistenceInput(
            identity_ref=manifest_path,
            represented_media_type=recognized_input_type.value,
            metadata=pipeline_result.metadata,
            relationships=[],
            manifest_ref=manifest_path,
            registration_status=None,
            storage_path=pipeline_result.stored_path,
            source_url=(
                text
                if recognized_input_type
                in (InputType.WEB_LINK, InputType.YOUTUBE_LINK)
                else None
            ),
        )
        registry_client = (
            registry
            if registry is not None
            else PostgresRegistry.from_environment()
        )
        try:
            persisted = await registry_client.register(persistence_input)
        except RegistryPersistenceError:
            pass
        else:
            registration_succeeded = True
            registry_record_id = persisted.record_id
            if domain_event is not None:
                if event_engine is None:
                    raise ValueError(
                        "event_engine is required when domain_event is supplied"
                    )
                envelope = EventEnvelope(
                    event=domain_event,
                    aggregate_id=None,
                    correlation_id=None,
                    causation_id=None,
                    schema_version=event_schema_version,
                )
                event_publication_attempted = True
                delivery_result = await event_engine.process(envelope)
                event_delivery_succeeded = delivery_result.success
                event_delivery_failure_code = delivery_result.failure_code

    return IngestionResult(
        input_type=input_type,
        recognized_input_type=recognized_input_type,
        stored_path=pipeline_result.stored_path,
        manifest_path=pipeline_result.manifest_path,
        metadata=pipeline_result.metadata,
        text=text,
        register_handoff_ready=pipeline_result.register_handoff_ready,
        process_handoff_ready=False,
        route_handoff_ready=False,
        respond_acknowledgement_ready=True,
        registration_succeeded=registration_succeeded,
        registry_record_id=registry_record_id,
        event_publication_attempted=event_publication_attempted,
        event_delivery_succeeded=event_delivery_succeeded,
        event_delivery_failure_code=event_delivery_failure_code,
    )
