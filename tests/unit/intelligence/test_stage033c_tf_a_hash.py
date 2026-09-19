import copy
import hashlib
import json
import tempfile
import unittest
import sys
import unicodedata
from datetime import date, datetime
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
    ITEM_FIELDS = (
        "line_number", "candidate_material_description", "canonical_display_name",
        "size_description", "specification", "material_id", "full_colly_count",
        "qty_per_full_colly", "partial_qty", "total_qty", "unit",
    )

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return matrix.fixture(temporary.name)

    def raw_digest(self, trusted):
        return hashlib.sha256(canon(trusted)).hexdigest()

    def dto_value(self, facts):
        decimal_text = lambda value: None if value is None else format(value, "f")
        return {
            "supplier_name": facts.supplier_name,
            "document_number": facts.document_number,
            "document_date": facts.document_date.isoformat() if facts.document_date else None,
            "received_at": facts.received_at.isoformat(),
            "items": [{
                "line_number": item.line_number,
                "candidate_material_description": item.candidate_material_description,
                "canonical_display_name": item.canonical_display_name,
                "size_description": item.size_description,
                "specification": item.specification,
                "material_id": str(item.material_id) if item.material_id else None,
                "full_colly_count": item.full_colly_count,
                "qty_per_full_colly": decimal_text(item.qty_per_full_colly),
                "partial_qty": decimal_text(item.partial_qty),
                "total_qty": decimal_text(item.total_qty),
                "unit": item.unit,
            } for item in facts.items],
        }

    def dto_bytes(self, facts):
        return json.dumps(self.dto_value(facts), ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")

    def rich_trusted(self):
        trusted = self.fixture()["input"]["trusted_receipt_facts"]
        trusted.update(
            supplier_name="Pemasok Éxample", document_number="箱 EF",
            document_date="2030-01-02", received_at="2030-01-02T03:04:05.123456Z",
            items=[{
                "line_number": 20, "candidate_material_description": "Lembaran É pertama",
                "canonical_display_name": "Kanon 箱 A", "size_description": "Ukuran Ω",
                "specification": "Spesifikasi α", "material_id": None,
                "full_colly_count": 2, "qty_per_full_colly": "3", "partial_qty": "1",
                "total_qty": "7", "unit": "sheet",
            }, {
                "line_number": 7, "candidate_material_description": "Bahan kedua",
                "canonical_display_name": "Kanon β", "size_description": "Dimensi 二",
                "specification": "Mutu γ",
                "material_id": "12345678-1234-4abc-8def-1234567890ab",
                "full_colly_count": 1, "qty_per_full_colly": "1.234567",
                "partial_qty": "0.000001", "total_qty": "1.234568", "unit": "kg",
            }],
        )
        return trusted

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
        trusted["received_at"] = "2030-01-02T03:04:05.000000Z"
        captured = []
        with patch(
            "core.app.material_receipts.candidate_create_authorization.trusted_facts_sha256",
            side_effect=lambda facts: captured.append(facts) or trusted_facts_sha256(facts),
        ):
            m.trusted_facts_dto_sha256(trusted)
        projected = captured[0]
        self.assertEqual(projected.received_at.isoformat(), "2030-01-02T03:04:05+00:00")
        self.assertEqual(self.dto_value(projected)["received_at"],
                         "2030-01-02T03:04:05+00:00")
        source_datetime = m.parse_utc("2030-01-02T03:04:05.000000Z")
        dto_datetime = datetime.fromisoformat("2030-01-02T03:04:05+00:00")
        self.assertEqual(source_datetime, dto_datetime)
        self.assertEqual(projected.received_at, source_datetime)

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

    def test_14_all_five_receipt_fields_preserved(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        self.assertEqual(facts.supplier_name, trusted["supplier_name"])
        self.assertEqual(facts.document_number, trusted["document_number"])
        self.assertEqual(facts.document_date, date.fromisoformat(trusted["document_date"]))
        self.assertEqual(facts.received_at, m.parse_utc(trusted["received_at"]))
        self.assertEqual(len(facts.items), len(trusted["items"]))

    def test_15_all_eleven_fields_of_every_item_preserved(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        for source, item in zip(trusted["items"], facts.items, strict=True):
            self.assertEqual(item.line_number, source["line_number"])
            self.assertEqual(item.candidate_material_description, source["candidate_material_description"])
            self.assertEqual(item.canonical_display_name, source["canonical_display_name"])
            self.assertEqual(item.size_description, source["size_description"])
            self.assertEqual(item.specification, source["specification"])
            self.assertEqual(str(item.material_id) if item.material_id else None, source["material_id"])
            self.assertEqual(item.full_colly_count, source["full_colly_count"])
            self.assertEqual(item.qty_per_full_colly, Decimal(source["qty_per_full_colly"]))
            self.assertEqual(item.partial_qty, Decimal(source["partial_qty"]))
            self.assertEqual(item.total_qty, Decimal(source["total_qty"]))
            self.assertEqual(item.unit, source["unit"])

    def test_16_count_order_and_nonsorted_line_numbers_preserved(self):
        facts = self.projected(self.rich_trusted())
        self.assertEqual(len(facts.items), 2)
        self.assertEqual([item.line_number for item in facts.items], [20, 7])
        self.assertEqual([item.candidate_material_description for item in facts.items],
                         ["Lembaran É pertama", "Bahan kedua"])

    def test_17_null_and_nonnull_material_ids_preserved(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        self.assertIsNone(facts.items[0].material_id)
        self.assertEqual(str(facts.items[1].material_id), trusted["items"][1]["material_id"])

    def test_18_unicode_is_exact_utf8_and_not_ascii_escaped(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        encoded = self.dto_bytes(facts)
        for value in ("Pemasok Éxample", "箱 EF", "Ukuran Ω"):
            self.assertIn(value.encode("utf-8"), encoded)
        for escape in (b"\\u00c9", b"\\u7bb1", b"\\u03a9"):
            self.assertNotIn(escape, encoded)
        self.assertEqual(facts.supplier_name, trusted["supplier_name"])
        self.assertEqual(facts.items[0].size_description, trusted["items"][0]["size_description"])

    def test_19_nonzero_microseconds_exact_governed_form_and_semantics(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        self.assertEqual(facts.received_at.isoformat(), "2030-01-02T03:04:05.123456+00:00")
        self.assertEqual(self.dto_value(facts)["received_at"],
                         "2030-01-02T03:04:05.123456+00:00")
        self.assertEqual(facts.received_at, m.parse_utc(trusted["received_at"]))
        self.assertNotEqual(self.raw_digest(trusted), m.trusted_facts_dto_sha256(trusted))

    def test_20_three_projection_byte_and_digest_runs_are_identical(self):
        trusted = self.rich_trusted()
        projections = [self.projected(copy.deepcopy(trusted)) for _ in range(3)]
        encoded = [self.dto_bytes(facts) for facts in projections]
        digests = [m.trusted_facts_dto_sha256(copy.deepcopy(trusted)) for _ in range(3)]
        self.assertEqual(encoded, [encoded[0]] * 3)
        self.assertEqual(digests, [digests[0]] * 3)
        self.assertEqual(digests[0], hashlib.sha256(encoded[0]).hexdigest())

    def test_21_whole_fractional_decimals_and_units_preserved(self):
        facts = self.projected(self.rich_trusted())
        self.assertEqual((facts.items[0].qty_per_full_colly, facts.items[0].total_qty),
                         (Decimal("3"), Decimal("7")))
        self.assertEqual((facts.items[1].qty_per_full_colly, facts.items[1].partial_qty,
                          facts.items[1].total_qty),
                         (Decimal("1.234567"), Decimal("0.000001"), Decimal("1.234568")))
        self.assertEqual([item.unit for item in facts.items], ["sheet", "kg"])
        projected_items = self.dto_value(facts)["items"]
        self.assertEqual(projected_items[0]["qty_per_full_colly"], "3")
        self.assertEqual(projected_items[1]["qty_per_full_colly"], "1.234567")

    def test_22_nullable_and_nonnull_document_fields_preserved(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        self.assertEqual(facts.document_number, "箱 EF")
        self.assertEqual(facts.document_date, date(2030, 1, 2))
        trusted["document_number"] = None
        trusted["document_date"] = None
        facts = self.projected(trusted)
        self.assertIsNone(facts.document_number)
        self.assertIsNone(facts.document_date)

    def test_23_comprehensive_source_to_dto_no_business_value_drift(self):
        trusted = self.rich_trusted()
        facts = self.projected(trusted)
        projected = self.dto_value(facts)
        self.assertEqual(projected["supplier_name"], trusted["supplier_name"])
        self.assertEqual(projected["document_number"], trusted["document_number"])
        self.assertEqual(projected["document_date"], trusted["document_date"])
        # Intentional representation-only change: Z lexical input is parsed to a
        # semantic datetime, then datetime.isoformat() emits governed +00:00.
        self.assertEqual(facts.received_at, m.parse_utc(trusted["received_at"]))
        self.assertEqual(projected["received_at"], "2030-01-02T03:04:05.123456+00:00")
        self.assertEqual(len(projected["items"]), len(trusted["items"]))
        for source, item in zip(trusted["items"], projected["items"], strict=True):
            for field in self.ITEM_FIELDS:
                self.assertEqual(item[field], source[field], field)

    def test_24_hash_roles_are_independent_and_exact(self):
        fixture = self.fixture()
        semantic, transport = fixture["input_transport"][:-1], fixture["input_transport"]
        payload = fixture["approval"]["package_payload"]
        expected = {
            "trusted_facts_sha256": m.trusted_facts_dto_sha256(fixture["input"]["trusted_receipt_facts"]),
            "input_semantic_sha256": hashlib.sha256(semantic).hexdigest(),
            "input_transport_sha256": hashlib.sha256(transport).hexdigest(),
        }
        self.assertEqual({key: payload[key] for key in expected}, expected)
        self.assertEqual(len(set(expected.values())), 3)
        for key in expected:
            changed = self.fixture()
            changed["approval"]["package_payload"][key] = "0" * 64
            with self.subTest(key=key):
                matrix.invalid(self, changed)

    def test_25_rich_tf_a_approval_accepted_and_raw_rejected_before_claim(self):
        fixture = self.fixture()
        fixture["input"]["trusted_receipt_facts"] = self.rich_trusted()
        payload = fixture["approval"]["package_payload"]
        payload["item_count"] = 2
        payload["trusted_fact_provenance"] = {
            key: "EVIDENCE_DERIVED" for key in m.expected_provenance_pointers(2)
        }
        matrix.refresh(fixture)
        matrix.validate(fixture)
        payload["trusted_facts_sha256"] = self.raw_digest(fixture["input"]["trusted_receipt_facts"])
        with patch.object(m, "durable_claim", side_effect=AssertionError("claim reached")):
            with self.assertRaises(m.GovernedStop) as caught:
                matrix.validate(fixture)
        self.assertEqual(caught.exception.classification, m.APPROVED_BYTES_INVALID)
        self.assertEqual(caught.exception.stage, "TRUSTED_FACTS_HASH")

    def test_26_normalization_sensitive_unicode_is_preserved_exactly(self):
        nfc = "é"
        nfd = "e\u0301"
        self.assertEqual(unicodedata.normalize("NFC", nfd), nfc)
        self.assertNotEqual(nfc, nfd)

        trusted_by_form = {}
        facts_by_form = {}
        bytes_by_form = {}
        digest_by_form = {}
        for form, value in (("NFC", nfc), ("NFD", nfd)):
            with self.subTest(unicode_form=form):
                trusted = self.rich_trusted()
                trusted["supplier_name"] = value
                facts = self.projected(trusted)
                encoded = self.dto_bytes(facts)
                digest = m.trusted_facts_dto_sha256(trusted)

                self.assertEqual(facts.supplier_name, trusted["supplier_name"])
                self.assertEqual(facts.supplier_name, value)
                self.assertIn(value.encode("utf-8"), encoded)
                self.assertNotIn(b"\\ufffd", encoded)
                self.assertNotIn(b"\xef\xbf\xbd", encoded)
                self.assertNotIn(b"\\u00e9", encoded)
                self.assertNotIn(b"\\u0301", encoded)

                trusted_by_form[form] = trusted
                facts_by_form[form] = facts
                bytes_by_form[form] = encoded
                digest_by_form[form] = digest

        self.assertEqual(facts_by_form["NFD"].supplier_name, "e\u0301")
        self.assertEqual(facts_by_form["NFD"].supplier_name.encode("utf-8"),
                         b"e\xcc\x81")
        self.assertNotEqual(facts_by_form["NFD"].supplier_name,
                            facts_by_form["NFC"].supplier_name)
        self.assertNotEqual(bytes_by_form["NFC"], bytes_by_form["NFD"])
        self.assertNotEqual(digest_by_form["NFC"], digest_by_form["NFD"])
        self.assertEqual(
            set(trusted_by_form["NFC"]) - {"supplier_name"},
            set(trusted_by_form["NFD"]) - {"supplier_name"},
        )
        for key in set(trusted_by_form["NFC"]) - {"supplier_name"}:
            self.assertEqual(trusted_by_form["NFC"][key], trusted_by_form["NFD"][key])
