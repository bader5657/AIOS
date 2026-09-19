import copy
import hashlib
import json
import tempfile
import unittest
import sys
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT))

from core.app.material_receipts.candidate_create_authorization import trusted_facts_sha256
from tests.unit.intelligence import test_stage033c_registry_manifest_matrix as matrix


m = matrix.m
canon = matrix.canon


class TfADtoProjectionHashTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return matrix.fixture(temporary.name)

    def raw_digest(self, trusted):
        return hashlib.sha256(canon(trusted)).hexdigest()

    def test_01_valid_tf_a_projection_digest_accepted(self):
        matrix.validate(self.fixture())

    def test_02_raw_subobject_digest_differs_for_timestamp_representation(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        self.assertNotEqual(self.raw_digest(trusted), m.trusted_facts_dto_sha256(trusted))

    def test_03_approval_carrying_raw_subobject_digest_rejected(self):
        fixture = self.fixture()
        fixture["approval"]["package_payload"]["trusted_facts_sha256"] = self.raw_digest(
            fixture["input"]["trusted_receipt_facts"]
        )
        matrix.invalid(self, fixture)

    def test_04_harness_z_timestamp_maps_to_same_semantic_datetime(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        captured = []
        with patch(
            "core.app.material_receipts.candidate_create_authorization.trusted_facts_sha256",
            side_effect=lambda facts: captured.append(facts) or trusted_facts_sha256(facts),
        ):
            m.trusted_facts_dto_sha256(trusted)
        self.assertEqual(captured[0].received_at, m.parse_utc(trusted["received_at"]))

    def test_05_zero_microsecond_uses_governed_isoformat(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        trusted["received_at"] = "2026-08-18T10:11:12.000000Z"
        captured = []
        with patch(
            "core.app.material_receipts.candidate_create_authorization.trusted_facts_sha256",
            side_effect=lambda facts: captured.append(facts) or trusted_facts_sha256(facts),
        ):
            m.trusted_facts_dto_sha256(trusted)
        self.assertEqual(captured[0].received_at.isoformat(), "2026-08-18T10:11:12+00:00")

    def test_06_nonzero_microseconds_are_deterministic(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        first = m.trusted_facts_dto_sha256(trusted)
        second = m.trusted_facts_dto_sha256(copy.deepcopy(trusted))
        self.assertEqual(first, second)

    def test_07_input_semantic_hash_is_independent(self):
        fixture = self.fixture()
        fixture["approval"]["package_payload"]["input_semantic_sha256"] = "0" * 64
        matrix.invalid(self, fixture)

    def test_08_input_transport_hash_is_independent(self):
        fixture = self.fixture()
        fixture["approval"]["package_payload"]["input_transport_sha256"] = "0" * 64
        matrix.invalid(self, fixture)

    def projected(self, trusted):
        captured = []
        with patch(
            "core.app.material_receipts.candidate_create_authorization.trusted_facts_sha256",
            side_effect=lambda facts: captured.append(facts) or trusted_facts_sha256(facts),
        ):
            m.trusted_facts_dto_sha256(trusted)
        return captured[0]

    def test_09_business_facts_unchanged_by_projection(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        facts = self.projected(trusted)
        self.assertEqual((facts.supplier_name, facts.document_number), (trusted["supplier_name"], trusted["document_number"]))

    def test_10_item_order_preserved(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        second = copy.deepcopy(trusted["items"][0])
        second.update(line_number=2, candidate_material_description="Second")
        trusted["items"].append(second)
        self.assertEqual([item.line_number for item in self.projected(trusted).items], [1, 2])

    def test_11_decimal_quantities_preserved_without_rounding(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        trusted["items"][0].update(qty_per_full_colly="1.234567", partial_qty="0.000001", total_qty="1.234568")
        item = self.projected(trusted).items[0]
        self.assertEqual((item.qty_per_full_colly, item.partial_qty, item.total_qty), (Decimal("1.234567"), Decimal("0.000001"), Decimal("1.234568")))

    def test_12_unit_preserved(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        self.assertEqual(self.projected(trusted).items[0].unit, "pcs")

    def test_13_material_id_and_null_preserved(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        self.assertIsNone(self.projected(trusted).items[0].material_id)
        trusted["items"][0]["material_id"] = "12345678-1234-4abc-8def-1234567890ab"
        self.assertEqual(str(self.projected(trusted).items[0].material_id), trusted["items"][0]["material_id"])
