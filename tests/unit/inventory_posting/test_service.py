from dataclasses import FrozenInstanceError
from decimal import Decimal
import inspect
import unittest
import uuid
from unittest.mock import AsyncMock, patch

from psycopg import conninfo

from core.inventory_posting import (
    InventoryPostingError, InventoryPostingFailureCode, MovementEvidence,
    PostConfirmedReceiptRequest,
)
from core.inventory_posting.repository import (
    InventoryPostingRepository,
    PostingDatabaseConfig,
)
from core.inventory_posting.service import InventoryPostingService


class PostingServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_narrow_operation_delegates(self):
        repository = AsyncMock(spec=InventoryPostingRepository)
        service = InventoryPostingService(repository)
        receipt_id = uuid.uuid4()
        await service.post_confirmed_receipt(receipt_id, 4, "operator:1")
        repository.post_confirmed_receipt.assert_awaited_once_with(
            receipt_id, 4, "operator:1"
        )

    def test_request_and_evidence_are_frozen(self):
        request = PostConfirmedReceiptRequest(uuid.uuid4(), 1, "operator:1")
        with self.assertRaises(FrozenInstanceError):
            request.expected_version = 2
        evidence = MovementEvidence(
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Decimal("1"), "sheet",
            Decimal("0"), Decimal("1"),
        )
        with self.assertRaises(FrozenInstanceError):
            evidence.unit = "kg"

    def test_only_authoritative_mutation_surface_exists(self):
        for name in ("execute_sql", "update_stock", "create_movement", "delete", "save"):
            self.assertFalse(hasattr(InventoryPostingRepository, name))
        source = inspect.getsource(InventoryPostingRepository).lower()
        self.assertIn("stock_qty = stock_qty + %s", source)
        self.assertNotIn("update inventory_movements", source)
        self.assertNotIn("delete from inventory_movements", source)
        self.assertNotIn("truncate", source)

    def test_item_defense_rejects_unresolved_and_invalid_formula(self):
        with self.assertRaises(InventoryPostingError) as caught:
            InventoryPostingRepository._validate_item(
                (uuid.uuid4(), None, 1, 1, Decimal("1"), Decimal("0"),
                 Decimal("1"), "sheet", "CONFIRMED")
            )
        self.assertEqual(caught.exception.code,
                         InventoryPostingFailureCode.MATERIAL_UNRESOLVED)
        with self.assertRaises(InventoryPostingError) as caught:
            InventoryPostingRepository._validate_item(
                (uuid.uuid4(), uuid.uuid4(), 1, 1, Decimal("2"), Decimal("0"),
                 Decimal("3"), "sheet", "CONFIRMED")
            )
        self.assertEqual(caught.exception.code,
                         InventoryPostingFailureCode.PACKAGING_FORMULA_INVALID)

    def test_posting_config_rejects_every_other_identity(self):
        for username in (
            "aios",
            "aios_material_receipt_candidate_runtime",
            "aios_material_stock_reader",
            "unexpected_user",
        ):
            with self.subTest(username=username), self.assertRaises(ValueError):
                PostingDatabaseConfig(password="test", username=username)

    def test_governed_environment_construction_uses_only_posting_identity(self):
        with patch.dict(
            "os.environ",
            {"AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD": "test-secret"},
            clear=True,
        ):
            repository = InventoryPostingRepository.from_environment()
        parsed = conninfo.conninfo_to_dict(repository._database_url)
        self.assertEqual(
            parsed["user"], "aios_material_inventory_posting_runtime"
        )
        self.assertEqual(parsed["host"], "127.0.0.1")
        self.assertEqual(parsed["port"], "5432")
        self.assertEqual(parsed["dbname"], "aios")
        self.assertNotIn("test-secret", repr(PostingDatabaseConfig("test-secret")))

    def test_unrestricted_database_url_is_not_a_constructor_seam(self):
        with self.assertRaises(TypeError):
            InventoryPostingRepository("postgresql://aios@127.0.0.1/aios")


if __name__ == "__main__":
    unittest.main()
