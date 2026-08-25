import os
import re
import unittest
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg import conninfo, sql


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
MATERIAL_STOCK_UP = (
    ROOT / "migrations/postgres/0002_create_material_stock.up.sql"
).read_text()
UP_PATH = (
    ROOT
    / "migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql"
)
DOWN_PATH = (
    ROOT
    / "migrations/postgres/0003_create_material_receipt_inventory_movement.down.sql"
)
UP = UP_PATH.read_text()
DOWN = DOWN_PATH.read_text()


def _sql_without_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", "", text)


class MaterialReceiptMovementMigrationStaticAuditTests(unittest.TestCase):
    def test_up_migration_has_exact_scope_and_no_prohibited_statements(self):
        sql_text = _sql_without_comments(UP).upper()
        prohibited = (
            "CASCADE",
            "CREATE ROLE",
            "ALTER ROLE",
            "CREATE USER",
            "GRANT",
            "REVOKE",
            "CREATE EXTENSION",
            "CREATE TRIGGER",
            "CREATE FUNCTION",
            "CREATE PROCEDURE",
            "INSERT INTO",
            "ALTER TABLE",
            "DROP ",
        )
        for construct in prohibited:
            with self.subTest(construct=construct):
                self.assertNotIn(construct, sql_text)

        self.assertEqual(len(re.findall(r"\bCREATE\s+TABLE\b", sql_text)), 3)
        self.assertEqual(len(re.findall(r"\bCREATE\s+INDEX\b", sql_text)), 5)
        for table in (
            "MATERIAL_RECEIPTS",
            "MATERIAL_RECEIPT_ITEMS",
            "INVENTORY_MOVEMENTS",
        ):
            self.assertRegex(sql_text, rf"CREATE\s+TABLE\s+{table}\s*\(")
        self.assertNotRegex(sql_text, r"CREATE\s+TABLE\s+MATERIAL_STOCK\b")
        self.assertNotRegex(sql_text, r"CREATE\s+TABLE\s+REGISTRY_RECORDS\b")

    def test_down_migration_has_exact_reverse_scope_without_cascade(self):
        statements = [
            statement.strip().upper()
            for statement in _sql_without_comments(DOWN).split(";")
            if statement.strip()
        ]
        self.assertEqual(
            statements,
            [
                "DROP TABLE INVENTORY_MOVEMENTS",
                "DROP TABLE MATERIAL_RECEIPT_ITEMS",
                "DROP TABLE MATERIAL_RECEIPTS",
            ],
        )
        self.assertNotIn("CASCADE", _sql_without_comments(DOWN).upper())
        self.assertNotIn("MATERIAL_STOCK", _sql_without_comments(DOWN).upper())
        self.assertNotIn("REGISTRY_RECORDS", _sql_without_comments(DOWN).upper())


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class MaterialReceiptMovementMigrationIntegrationTests(
    unittest.IsolatedAsyncioTestCase
):
    async def asyncSetUp(self):
        self.schema = "aios_material_receipt_migration_" + uuid.uuid4().hex
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        scoped_url = conninfo.make_conninfo(
            TEST_DATABASE_URL, options=f"-csearch_path={self.schema}"
        )
        self.connection = await psycopg.AsyncConnection.connect(
            scoped_url, autocommit=True
        )
        await self.connection.execute(MATERIAL_STOCK_UP)

    async def asyncTearDown(self):
        await self.connection.close()
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )

    async def _insert_material(self, **overrides):
        values = {
            "material_id": uuid.uuid4(),
            "name": "SH EF 630x560 K150/M125/M125",
            "stock_qty": Decimal("10.000000"),
            "unit": "sheet",
            "is_active": True,
            "updated_at": datetime.now(timezone.utc),
        }
        values.update(overrides)
        await self.connection.execute(
            """
            INSERT INTO material_stock
                (material_id, name, stock_qty, unit, is_active, updated_at)
            VALUES (%(material_id)s, %(name)s, %(stock_qty)s, %(unit)s,
                    %(is_active)s, %(updated_at)s)
            """,
            values,
        )
        return values["material_id"]

    async def _insert_receipt(self, **overrides):
        values = {
            "receipt_id": uuid.uuid4(),
            "supplier_name": "Supplier Test",
            "document_number": "SJ-TEST-001",
            "document_date": date(2026, 8, 25),
            "received_at": datetime.now(timezone.utc),
            "source_asset_reference": "asset:test:delivery-note",
        }
        values.update(overrides)
        columns = sql.SQL(", ").join(map(sql.Identifier, values))
        placeholders = sql.SQL(", ").join(sql.Placeholder(key) for key in values)
        await self.connection.execute(
            sql.SQL("INSERT INTO material_receipts ({}) VALUES ({})").format(
                columns, placeholders
            ),
            values,
        )
        return values["receipt_id"]

    async def _insert_item(self, receipt_id, **overrides):
        values = {
            "receipt_item_id": uuid.uuid4(),
            "receipt_id": receipt_id,
            "line_number": 1,
            "candidate_material_description": "SH EF test material",
            "full_colly_count": 1,
            "qty_per_full_colly": Decimal("50"),
            "partial_qty": Decimal("0"),
            "total_qty": Decimal("50"),
            "unit": "sheet",
        }
        values.update(overrides)
        columns = sql.SQL(", ").join(map(sql.Identifier, values))
        placeholders = sql.SQL(", ").join(sql.Placeholder(key) for key in values)
        await self.connection.execute(
            sql.SQL("INSERT INTO material_receipt_items ({}) VALUES ({})").format(
                columns, placeholders
            ),
            values,
        )
        return values["receipt_item_id"]

    async def _insert_movement(self, material_id, receipt_item_id, **overrides):
        values = {
            "movement_id": uuid.uuid4(),
            "material_id": material_id,
            "movement_type": "RECEIPT",
            "quantity_delta": Decimal("50"),
            "unit": "sheet",
            "source_receipt_item_id": receipt_item_id,
            "occurred_at": datetime.now(timezone.utc),
            "posting_actor_reference": "operator:test",
            "balance_before": Decimal("10"),
            "balance_after": Decimal("60"),
        }
        values.update(overrides)
        columns = sql.SQL(", ").join(map(sql.Identifier, values))
        placeholders = sql.SQL(", ").join(sql.Placeholder(key) for key in values)
        await self.connection.execute(
            sql.SQL("INSERT INTO inventory_movements ({}) VALUES ({})").format(
                columns, placeholders
            ),
            values,
        )
        return values["movement_id"]

    async def _columns(self, table):
        return await (
            await self.connection.execute(
                """
                SELECT column_name, data_type, udt_name, is_nullable,
                       column_default, numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
                """,
                (self.schema, table),
            )
        ).fetchall()

    async def _constraint_rows(self, table):
        return await (
            await self.connection.execute(
                """
                SELECT conname, contype, confupdtype, confdeltype,
                       pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid = %s::regclass
                ORDER BY conname
                """,
                (table,),
            )
        ).fetchall()

    async def test_exact_schema_constraints_indexes_and_prohibited_objects(self):
        roles_before = await (
            await self.connection.execute("SELECT rolname FROM pg_roles ORDER BY rolname")
        ).fetchall()
        await self.connection.execute(UP)

        expected_columns = {
            "material_receipts": [
                ("receipt_id", "uuid", "NO", None, None),
                ("supplier_name", "text", "NO", None, None),
                ("document_number", "text", "YES", None, None),
                ("document_date", "date", "YES", None, None),
                ("received_at", "timestamp with time zone", "NO", None, None),
                ("source_asset_reference", "text", "NO", None, None),
                ("status", "text", "NO", None, None),
                ("version", "integer", "NO", 32, 0),
                ("confirmed_version", "integer", "YES", 32, 0),
                ("confirmed_at", "timestamp with time zone", "YES", None, None),
                ("confirmation_actor_reference", "text", "YES", None, None),
                ("created_at", "timestamp with time zone", "NO", None, None),
                ("updated_at", "timestamp with time zone", "NO", None, None),
            ],
            "material_receipt_items": [
                ("receipt_item_id", "uuid", "NO", None, None),
                ("receipt_id", "uuid", "NO", None, None),
                ("line_number", "integer", "NO", 32, 0),
                ("candidate_material_description", "text", "YES", None, None),
                ("canonical_display_name", "text", "YES", None, None),
                ("size_description", "text", "YES", None, None),
                ("specification", "text", "YES", None, None),
                ("material_id", "uuid", "YES", None, None),
                ("full_colly_count", "integer", "NO", 32, 0),
                ("qty_per_full_colly", "numeric", "YES", 20, 6),
                ("partial_qty", "numeric", "NO", 20, 6),
                ("total_qty", "numeric", "NO", 20, 6),
                ("unit", "text", "NO", None, None),
                ("status", "text", "NO", None, None),
                ("created_at", "timestamp with time zone", "NO", None, None),
                ("updated_at", "timestamp with time zone", "NO", None, None),
            ],
            "inventory_movements": [
                ("movement_id", "uuid", "NO", None, None),
                ("material_id", "uuid", "NO", None, None),
                ("movement_type", "text", "NO", None, None),
                ("quantity_delta", "numeric", "NO", 20, 6),
                ("unit", "text", "NO", None, None),
                ("source_receipt_item_id", "uuid", "NO", None, None),
                ("occurred_at", "timestamp with time zone", "NO", None, None),
                ("posted_at", "timestamp with time zone", "NO", None, None),
                ("posting_actor_reference", "text", "NO", None, None),
                ("balance_before", "numeric", "NO", 20, 6),
                ("balance_after", "numeric", "NO", 20, 6),
                ("created_at", "timestamp with time zone", "NO", None, None),
            ],
        }
        for table, expected in expected_columns.items():
            with self.subTest(table=table):
                actual = await self._columns(table)
                projected = [
                    (row[0], row[1], row[3], row[5], row[6]) for row in actual
                ]
                self.assertEqual(projected, expected)

        defaults = {
            table: {row[0]: row[4] for row in await self._columns(table)}
            for table in expected_columns
        }
        self.assertIn("'EXTRACTED'::text", defaults["material_receipts"]["status"])
        self.assertEqual(defaults["material_receipts"]["version"], "1")
        self.assertIn("CURRENT_TIMESTAMP", defaults["material_receipts"]["created_at"])
        self.assertEqual(defaults["material_receipt_items"]["full_colly_count"], "0")
        self.assertEqual(defaults["material_receipt_items"]["partial_qty"], "0")
        self.assertIn("CURRENT_TIMESTAMP", defaults["inventory_movements"]["posted_at"])

        receipt_constraints = await self._constraint_rows("material_receipts")
        item_constraints = await self._constraint_rows("material_receipt_items")
        movement_constraints = await self._constraint_rows("inventory_movements")
        self.assertEqual(sum(row[1] == "p" for row in receipt_constraints), 1)
        self.assertEqual(sum(row[1] == "p" for row in item_constraints), 1)
        self.assertEqual(sum(row[1] == "p" for row in movement_constraints), 1)
        self.assertEqual(sum(row[1] == "u" for row in item_constraints), 1)
        self.assertEqual(sum(row[1] == "u" for row in movement_constraints), 1)

        for rows, expected_fk_count in ((receipt_constraints, 0), (item_constraints, 2), (movement_constraints, 2)):
            foreign_keys = [row for row in rows if row[1] == "f"]
            self.assertEqual(len(foreign_keys), expected_fk_count)
            for row in foreign_keys:
                self.assertEqual((row[2], row[3]), ("a", "a"))

        combined = " ".join(
            row[4] for row in receipt_constraints + item_constraints + movement_constraints
        ).lower()
        for fragment in (
            "confirmed_version = version",
            "full_colly_count",
            "coalesce(qty_per_full_colly",
            "material_id is not null",
            "movement_type",
            "balance_after = (balance_before + quantity_delta)",
            "source_receipt_item_id",
        ):
            self.assertIn(fragment, combined)
        for value in ("extracted", "needs_review", "confirmed", "posted", "rejected", "cancelled"):
            self.assertIn(value, combined)
        for unit in ("sheet", "pcs", "kg", "roll", "pack"):
            self.assertIn(unit, combined)

        indexes = await (
            await self.connection.execute(
                """
                SELECT tablename, indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = %s
                  AND tablename IN (
                      'material_receipts',
                      'material_receipt_items',
                      'inventory_movements'
                  )
                ORDER BY tablename, indexname
                """,
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(len(indexes), 10)
        index_names = {row[1] for row in indexes}
        self.assertTrue(
            {
                "material_receipts_status_idx",
                "material_receipts_document_lookup_idx",
                "material_receipts_source_asset_idx",
                "material_receipt_items_material_idx",
                "inventory_movements_material_posted_idx",
            }.issubset(index_names)
        )

        triggers = await (
            await self.connection.execute(
                """
                SELECT count(*)
                FROM pg_trigger t
                JOIN pg_class c ON c.oid = t.tgrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = %s AND NOT t.tgisinternal
                """,
                (self.schema,),
            )
        ).fetchone()
        self.assertEqual(triggers, (0,))
        routines = await (
            await self.connection.execute(
                "SELECT count(*) FROM information_schema.routines WHERE routine_schema = %s",
                (self.schema,),
            )
        ).fetchone()
        self.assertEqual(routines, (0,))
        roles_after = await (
            await self.connection.execute("SELECT rolname FROM pg_roles ORDER BY rolname")
        ).fetchall()
        self.assertEqual(roles_after, roles_before)

        tables = await (
            await self.connection.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = %s ORDER BY table_name",
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(
            tables,
            [
                ("inventory_movements",),
                ("material_receipt_items",),
                ("material_receipts",),
                ("material_stock",),
            ],
        )
        for table in ("material_receipts", "material_receipt_items", "inventory_movements"):
            count = await (
                await self.connection.execute(
                    sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
                )
            ).fetchone()
            self.assertEqual(count, (0,))

    async def test_receipt_lifecycle_version_and_confirmation_constraints(self):
        await self.connection.execute(UP)
        await self._insert_receipt()

        invalid_receipts = (
            {"supplier_name": "   "},
            {"supplier_name": "x" * 129},
            {"document_number": " SJ-1"},
            {"document_number": "x" * 129},
            {"source_asset_reference": "   "},
            {"status": "UNKNOWN"},
            {"version": 0},
            {"confirmed_version": 2, "version": 1, "confirmed_at": datetime.now(timezone.utc), "confirmation_actor_reference": "operator:test"},
            {"status": "CONFIRMED"},
            {"status": "NEEDS_REVIEW", "confirmed_version": 1, "confirmed_at": datetime.now(timezone.utc), "confirmation_actor_reference": "operator:test"},
            {"confirmed_version": 1},
        )
        for overrides in invalid_receipts:
            with self.subTest(overrides=overrides):
                with self.assertRaises(psycopg.errors.CheckViolation):
                    await self._insert_receipt(**overrides)

        for status in ("CONFIRMED", "POSTED"):
            with self.subTest(status=status):
                await self._insert_receipt(
                    status=status,
                    version=2,
                    confirmed_version=2,
                    confirmed_at=datetime.now(timezone.utc),
                    confirmation_actor_reference="operator:test",
                )
        await self._insert_receipt(
            status="REJECTED",
            confirmed_version=1,
            confirmed_at=datetime.now(timezone.utc),
            confirmation_actor_reference="operator:test",
        )

    async def test_packaging_examples_and_invalid_item_states(self):
        await self.connection.execute(UP)
        receipt_id = await self._insert_receipt()
        material_id = await self._insert_material()

        await self._insert_item(
            receipt_id,
            line_number=1,
            material_id=material_id,
            full_colly_count=125,
            qty_per_full_colly=Decimal("50"),
            partial_qty=Decimal("0"),
            total_qty=Decimal("6250"),
            status="CONFIRMED",
        )
        await self._insert_item(
            receipt_id,
            line_number=2,
            material_id=material_id,
            full_colly_count=62,
            qty_per_full_colly=Decimal("50"),
            partial_qty=Decimal("38"),
            total_qty=Decimal("3138"),
            status="CONFIRMED",
        )

        invalid_items = (
            {"full_colly_count": -1},
            {"full_colly_count": 1, "qty_per_full_colly": Decimal("0"), "total_qty": Decimal("1")},
            {"full_colly_count": 0, "qty_per_full_colly": Decimal("1"), "partial_qty": Decimal("1"), "total_qty": Decimal("1")},
            {"total_qty": Decimal("49")},
            {"qty_per_full_colly": Decimal("1.5"), "total_qty": Decimal("1.5")},
            {"full_colly_count": 0, "qty_per_full_colly": None, "partial_qty": Decimal("0"), "total_qty": Decimal("0")},
            {"unit": "box"},
            {"status": "CONFIRMED", "material_id": None},
        )
        for index, overrides in enumerate(invalid_items, start=10):
            with self.subTest(overrides=overrides):
                with self.assertRaises(psycopg.errors.CheckViolation):
                    await self._insert_item(receipt_id, line_number=index, **overrides)

        with self.assertRaises(psycopg.errors.UniqueViolation):
            await self._insert_item(receipt_id, line_number=1)

    async def test_movement_constraints_and_source_item_idempotency(self):
        await self.connection.execute(UP)
        receipt_id = await self._insert_receipt()
        material_id = await self._insert_material()
        item_id = await self._insert_item(
            receipt_id, material_id=material_id, status="CONFIRMED"
        )
        await self._insert_movement(material_id, item_id)

        with self.assertRaises(psycopg.errors.UniqueViolation):
            await self._insert_movement(material_id, item_id)

        invalid_movements = (
            {"movement_type": "ADJUSTMENT"},
            {"quantity_delta": Decimal("0"), "balance_after": Decimal("10")},
            {"quantity_delta": Decimal("-1"), "balance_after": Decimal("9")},
            {"unit": "box"},
            {"posting_actor_reference": "   "},
            {"balance_before": Decimal("-1"), "balance_after": Decimal("49")},
            {"balance_after": Decimal("59")},
            {"quantity_delta": Decimal("1.5"), "balance_after": Decimal("11.5")},
        )
        for index, overrides in enumerate(invalid_movements, start=2):
            next_item = await self._insert_item(
                receipt_id,
                line_number=index,
                material_id=material_id,
                status="CONFIRMED",
            )
            with self.subTest(overrides=overrides):
                with self.assertRaises(psycopg.errors.CheckViolation):
                    await self._insert_movement(material_id, next_item, **overrides)

    async def test_material_stock_preserved_by_up_down_and_reapply(self):
        material_id = await self._insert_material(stock_qty=Decimal("42.000000"))
        columns_before = await self._columns("material_stock")
        constraints_before = await self._constraint_rows("material_stock")
        data_before = await (
            await self.connection.execute(
                "SELECT * FROM material_stock WHERE material_id = %s", (material_id,)
            )
        ).fetchone()

        await self.connection.execute(UP)
        self.assertEqual(await self._columns("material_stock"), columns_before)
        self.assertEqual(await self._constraint_rows("material_stock"), constraints_before)
        self.assertEqual(
            await (
                await self.connection.execute(
                    "SELECT * FROM material_stock WHERE material_id = %s", (material_id,)
                )
            ).fetchone(),
            data_before,
        )

        await self.connection.execute(DOWN)
        for table in (
            "inventory_movements",
            "material_receipt_items",
            "material_receipts",
        ):
            self.assertEqual(
                await (
                    await self.connection.execute("SELECT to_regclass(%s)", (table,))
                ).fetchone(),
                (None,),
            )
        self.assertEqual(
            await (
                await self.connection.execute("SELECT to_regclass('material_stock')")
            ).fetchone(),
            ("material_stock",),
        )
        self.assertEqual(
            await (
                await self.connection.execute(
                    "SELECT * FROM material_stock WHERE material_id = %s", (material_id,)
                )
            ).fetchone(),
            data_before,
        )

        await self.connection.execute(UP)
        self.assertEqual(
            await (
                await self.connection.execute("SELECT to_regclass('material_receipts')")
            ).fetchone(),
            ("material_receipts",),
        )


if __name__ == "__main__":
    unittest.main()
