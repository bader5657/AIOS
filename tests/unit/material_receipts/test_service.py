import inspect
import unittest
import uuid
from unittest.mock import AsyncMock, patch

from psycopg import conninfo

from core.material_receipts.repository import (
    CandidateDatabaseConfig,
    MaterialReceiptRepository,
)
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

    def test_candidate_config_rejects_every_other_identity(self):
        for username in (
            "aios",
            "aios_material_inventory_posting_runtime",
            "aios_material_stock_reader",
            "unexpected_user",
        ):
            with self.subTest(username=username), self.assertRaises(ValueError):
                CandidateDatabaseConfig(password="test", username=username)

    def test_governed_environment_construction_uses_only_candidate_identity(self):
        with patch.dict(
            "os.environ",
            {"AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD": "test-secret"},
            clear=True,
        ):
            repository = MaterialReceiptRepository.from_environment()
        parsed = conninfo.conninfo_to_dict(repository._database_url)
        self.assertEqual(parsed["user"], "aios_material_receipt_candidate_runtime")
        self.assertEqual(parsed["host"], "127.0.0.1")
        self.assertEqual(parsed["port"], "5432")
        self.assertEqual(parsed["dbname"], "aios")
        self.assertNotIn("test-secret", repr(CandidateDatabaseConfig("test-secret")))

    def test_unrestricted_database_url_is_not_a_constructor_seam(self):
        with self.assertRaises(TypeError):
            MaterialReceiptRepository("postgresql://aios@127.0.0.1/aios")


if __name__ == "__main__":
    unittest.main()
