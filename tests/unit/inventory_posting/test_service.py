from dataclasses import FrozenInstanceError
from decimal import Decimal
import inspect
import unittest
import uuid
from unittest.mock import AsyncMock

from core.inventory_posting import (
    InventoryPostingError, InventoryPostingFailureCode, MovementEvidence,
    PostConfirmedReceiptRequest,
)
from core.inventory_posting.repository import InventoryPostingRepository
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


if __name__ == "__main__":
    unittest.main()
