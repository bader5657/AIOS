import inspect
import unittest
import uuid
from unittest.mock import AsyncMock

from core.material_receipts.repository import MaterialReceiptRepository
from core.material_receipts.service import MaterialReceiptService


class CandidateServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_operations_delegate_exactly(self):
        repository = AsyncMock(spec=MaterialReceiptRepository)
        service = MaterialReceiptService(repository)
        receipt_id, item_id = uuid.uuid4(), uuid.uuid4()
        await service.get_receipt_for_review(receipt_id)
        repository.get_receipt_for_review.assert_awaited_once_with(receipt_id)
        await service.confirm_receipt(receipt_id, 2, "operator:1")
        repository.confirm_receipt.assert_awaited_once_with(receipt_id, 2, "operator:1")
        await service.cancel_receipt_item(receipt_id, item_id, 2, "operator:1")
        repository.cancel_receipt_item.assert_awaited_once_with(
            receipt_id, item_id, 2, "operator:1"
        )

    def test_no_generic_or_delete_surface(self):
        for name in ("patch", "delete", "delete_item", "execute_sql", "save"):
            self.assertFalse(hasattr(MaterialReceiptRepository, name))
        source = inspect.getsource(MaterialReceiptRepository).lower()
        self.assertNotIn("delete from", source)
        self.assertNotIn("inventory_movements", source)
        self.assertNotIn("update material_stock", source)


if __name__ == "__main__":
    unittest.main()
