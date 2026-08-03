import ast
import inspect
import json
import unittest
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from core.app import request_context
from core.app.request_context import RequestContext


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_PATH = REPOSITORY_ROOT / "core/app/request_context.py"
CONFIGURATION_PATH = REPOSITORY_ROOT / "config/request-context.schema.json"

ACTIVE_FIELD_TYPES = {
    "source": str,
    "user_id": int,
    "chat_id": int,
    "message_id": int,
    "username": str,
    "text": str,
    "received_at": datetime,
}

RESERVED_RUNTIME_FIELDS = {
    "schema_version",
    "request_id",
    "conversation_id",
    "parent_request_id",
    "gateway",
    "display_name",
    "language",
    "timezone",
    "message_type",
    "raw_text",
    "normalized_text",
    "attachments",
    "links",
    "current_priority",
    "conversation_summary",
    "related_entity_type",
    "related_entity_id",
    "selected_mode",
    "selected_specialist",
    "confidence",
    "requires_clarification",
    "clarification_question",
    "status",
    "requires_confirmation",
    "approved",
    "memory_candidate",
    "processed_at",
}


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 8, 3, 15, 4, 5, tzinfo=tz)


class RequestContextSchemaConformanceTests(unittest.TestCase):
    def test_runtime_has_exact_active_field_schema(self):
        self.assertEqual(
            [field.name for field in fields(RequestContext)],
            list(ACTIVE_FIELD_TYPES),
        )
        self.assertEqual(get_type_hints(RequestContext), ACTIVE_FIELD_TYPES)

    def test_flat_serialization_conforms_to_active_schema(self):
        received_at = datetime(2026, 8, 3, 8, 4, 5, tzinfo=timezone.utc)
        context = RequestContext(
            source="telegram",
            user_id=11,
            chat_id=22,
            message_id=33,
            username="operator",
            text="payload",
            received_at=received_at,
        )

        self.assertEqual(
            context.to_dict(),
            {
                "source": "telegram",
                "user_id": 11,
                "chat_id": 22,
                "message_id": 33,
                "username": "operator",
                "text": "payload",
                "received_at": "2026-08-03T08:04:05+00:00",
            },
        )

    def test_configuration_only_fields_remain_reserved(self):
        configuration = json.loads(
            CONFIGURATION_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(configuration),
            {
                "schema_version",
                "request_id",
                "conversation_id",
                "parent_request_id",
                "source",
                "user",
                "input",
                "context",
                "routing",
                "processing",
                "timestamps",
            },
        )
        self.assertTrue(
            RESERVED_RUNTIME_FIELDS.isdisjoint(
                field.name for field in fields(RequestContext)
            )
        )


class RequestContextCompatibilityTests(unittest.TestCase):
    def test_telegram_factory_signature_remains_keyword_only(self):
        parameters = inspect.signature(RequestContext.from_telegram).parameters
        self.assertEqual(
            list(parameters),
            ["user_id", "chat_id", "message_id", "username", "text"],
        )
        self.assertTrue(
            all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY
                for parameter in parameters.values()
            )
        )

    def test_telegram_factory_preserves_values_and_creates_utc_time(self):
        with patch.object(request_context, "datetime", FixedDateTime):
            context = RequestContext.from_telegram(
                user_id=11,
                chat_id=22,
                message_id=33,
                username="operator",
                text="payload",
            )

        self.assertEqual(context.source, "telegram")
        self.assertEqual(context.user_id, 11)
        self.assertEqual(context.chat_id, 22)
        self.assertEqual(context.message_id, 33)
        self.assertEqual(context.username, "operator")
        self.assertEqual(context.text, "payload")
        self.assertEqual(
            context.received_at,
            FixedDateTime(2026, 8, 3, 15, 4, 5, tzinfo=timezone.utc),
        )

    def test_runtime_has_no_downstream_dependency_or_reserved_behavior(self):
        tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        defined_attributes = {
            node.target.id
            for node in ast.walk(tree)
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
        }

        self.assertEqual(
            imported_modules,
            {"dataclasses", "datetime", "typing"},
        )
        self.assertTrue(RESERVED_RUNTIME_FIELDS.isdisjoint(defined_attributes))


if __name__ == "__main__":
    unittest.main()
