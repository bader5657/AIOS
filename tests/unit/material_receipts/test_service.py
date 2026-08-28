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
    def test_creator_less_and_raw_actor_create_surfaces_are_absent(self):
        self.assertFalse(hasattr(MaterialReceiptService, "create_receipt_candidate"))
        self.assertFalse(hasattr(MaterialReceiptRepository, "create_receipt_candidate"))
        public = {name for name in dir(MaterialReceiptRepository) if not name.startswith("_")}
        self.assertFalse(public & {"create", "save", "insert", "execute", "dispatch", "run", "handle"})
        self.assertTrue(hasattr(MaterialReceiptRepository, "_create_receipt_candidate"))
        for name in (
            "create", "save", "insert", "execute", "execute_sql", "dispatch",
            "invoke", "run", "handle", "repository", "get_repository",
            "database_url", "delete",
        ):
            self.assertFalse(hasattr(MaterialReceiptService, name))
        source = inspect.getsource(MaterialReceiptService)
        self.assertNotIn("ActorContext", source)
        self.assertNotIn("created_by_actor_reference", source)
        self.assertNotIn("actor_provenance", source)

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
        for name in ("revise_receipt_candidate", "get_receipt_for_review", "confirm_receipt", "reject_receipt", "cancel_receipt", "cancel_receipt_item"):
            self.assertTrue(hasattr(service, name))
        self.assertTrue(hasattr(service, "revise_receipt_candidate"))
        self.assertTrue(hasattr(service, "get_receipt_for_review"))
        self.assertTrue(hasattr(service, "confirm_receipt"))
        self.assertTrue(hasattr(service, "reject_receipt"))
        self.assertTrue(hasattr(service, "cancel_receipt"))
        self.assertTrue(hasattr(service, "cancel_receipt_item"))

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
