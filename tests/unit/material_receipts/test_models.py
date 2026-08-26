from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from decimal import Decimal
import unittest
import uuid

from core.material_receipts import (
    MaterialReceiptError,
    MaterialReceiptFailureCode,
    ReceiptCandidateRequest,
    ReceiptItemCandidate,
)


def item(**overrides):
    values = dict(
        receipt_item_id=uuid.uuid4(), line_number=1,
        candidate_material_description="EF sheet", canonical_display_name=None,
        size_description=None, specification=None, material_id=None,
        full_colly_count=125, qty_per_full_colly=Decimal("50"),
        partial_qty=Decimal("0"), total_qty=Decimal("6250"), unit="sheet",
    )
    values.update(overrides)
    return ReceiptItemCandidate(**values)


def request(*items):
    return ReceiptCandidateRequest(
        uuid.uuid4(), "Supplier", None, None, datetime.now(timezone.utc),
        "asset:test", tuple(items or (item(),)),
    )


class ReceiptModelTests(unittest.TestCase):
    def test_packaging_examples(self):
        self.assertEqual(item().total_qty, Decimal("6250"))
        loose = item(full_colly_count=62, partial_qty=Decimal("38"),
                     total_qty=Decimal("3138"))
        self.assertEqual(loose.total_qty, Decimal("3138"))

    def test_formula_mismatch(self):
        with self.assertRaises(MaterialReceiptError) as caught:
            item(total_qty=Decimal("6249"))
        self.assertEqual(caught.exception.code,
                         MaterialReceiptFailureCode.PACKAGING_FORMULA_INVALID)

    def test_fractional_sheet_and_invalid_unit(self):
        with self.assertRaises(ValueError):
            item(full_colly_count=0, qty_per_full_colly=None,
                 partial_qty=Decimal("1.5"), total_qty=Decimal("1.5"))
        with self.assertRaises(ValueError):
            item(unit="colly")

    def test_duplicate_lines_and_ids(self):
        first = item()
        with self.assertRaises(ValueError):
            request(first, item(line_number=1))
        with self.assertRaises(ValueError):
            request(first, item(receipt_item_id=first.receipt_item_id, line_number=2))

    def test_unresolved_material_is_allowed_and_dtos_are_frozen(self):
        candidate = request(item(material_id=None))
        self.assertIsNone(candidate.items[0].material_id)
        with self.assertRaises(FrozenInstanceError):
            candidate.supplier_name = "changed"
        self.assertNotIn("status", [field.name for field in fields(ReceiptItemCandidate)])
        for prohibited in ("sql", "database_url", "password", "balance_before"):
            self.assertNotIn(prohibited, [field.name for field in fields(ReceiptCandidateRequest)])


if __name__ == "__main__":
    unittest.main()
