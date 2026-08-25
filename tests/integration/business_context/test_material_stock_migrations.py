import os
import re
import unittest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg import conninfo, sql


TEST_DATABASE_URL = os.environ.get("AIOS_REGISTRY_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
UP_PATH = ROOT / "migrations/postgres/0002_create_material_stock.up.sql"
DOWN_PATH = ROOT / "migrations/postgres/0002_create_material_stock.down.sql"
UP = UP_PATH.read_text()
DOWN = DOWN_PATH.read_text()


def _sql_without_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", "", text)


class MaterialStockMigrationStaticAuditTests(unittest.TestCase):
    def test_up_migration_has_no_prohibited_statements(self):
        sql_text = _sql_without_comments(UP).upper()
        prohibited = (
            "CASCADE",
            "CREATE ROLE",
            "ALTER ROLE",
            "GRANT",
            "REVOKE",
            "CREATE EXTENSION",
            "CREATE TRIGGER",
            "CREATE FUNCTION",
            "CREATE PROCEDURE",
            "INSERT",
            "ALTER TABLE",
            "DROP ",
        )
        for construct in prohibited:
            with self.subTest(construct=construct):
                self.assertNotIn(construct, sql_text)
        self.assertEqual(len(re.findall(r"\bCREATE\s+TABLE\b", sql_text)), 1)
        self.assertRegex(sql_text, r"CREATE\s+TABLE\s+MATERIAL_STOCK\s*\(")

    def test_down_migration_only_drops_material_stock_without_cascade(self):
        sql_text = _sql_without_comments(DOWN).strip().upper()
        self.assertEqual(sql_text, "DROP TABLE MATERIAL_STOCK;")
        self.assertNotIn("CASCADE", sql_text)


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "AIOS_REGISTRY_TEST_DATABASE_URL is required for isolated PostgreSQL tests",
)
class MaterialStockMigrationIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema = "aios_material_stock_migration_" + uuid.uuid4().hex
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

    async def asyncTearDown(self):
        await self.connection.close()
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )

    async def _insert(self, **overrides):
        values = {
            "material_id": uuid.uuid4(),
            "name": "Aluminium sheet",
            "stock_qty": Decimal("1.000000"),
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

    async def test_schema_contract_and_prohibited_objects(self):
        before_roles = await (
            await self.connection.execute("SELECT rolname FROM pg_roles ORDER BY rolname")
        ).fetchall()
        await self.connection.execute(UP)

        columns = await (
            await self.connection.execute(
                """
                SELECT column_name, data_type, udt_name, is_nullable,
                       column_default, numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = 'material_stock'
                ORDER BY ordinal_position
                """,
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(
            columns,
            [
                ("material_id", "uuid", "uuid", "NO", None, None, None),
                ("name", "text", "text", "NO", None, None, None),
                ("stock_qty", "numeric", "numeric", "NO", None, 20, 6),
                ("unit", "text", "text", "NO", None, None, None),
                ("is_active", "boolean", "bool", "NO", None, None, None),
                (
                    "updated_at",
                    "timestamp with time zone",
                    "timestamptz",
                    "NO",
                    None,
                    None,
                    None,
                ),
            ],
        )
        constraints = await (
            await self.connection.execute(
                """
                SELECT contype, pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid = 'material_stock'::regclass
                ORDER BY contype, conname
                """
            )
        ).fetchall()
        self.assertEqual([row[0] for row in constraints], ["c", "c", "c", "p"])
        definitions = " ".join(row[1] for row in constraints).lower()
        self.assertIn("primary key (material_id)", definitions)
        self.assertIn("btrim(name)", definitions)
        self.assertIn("stock_qty >=", definitions)
        for unit in ("sheet", "pcs", "kg", "roll", "pack"):
            self.assertIn(unit, definitions)

        foreign_keys = await (
            await self.connection.execute(
                "SELECT count(*) FROM pg_constraint "
                "WHERE conrelid = 'material_stock'::regclass AND contype = 'f'"
            )
        ).fetchone()
        self.assertEqual(foreign_keys, (0,))
        indexes = await (
            await self.connection.execute(
                "SELECT indexdef FROM pg_indexes "
                "WHERE schemaname = %s AND tablename = 'material_stock'",
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(len(indexes), 1)
        self.assertIn("UNIQUE INDEX", indexes[0][0])
        self.assertIn("(material_id)", indexes[0][0])
        triggers = await (
            await self.connection.execute(
                """
                SELECT count(*) FROM pg_trigger
                WHERE tgrelid = 'material_stock'::regclass AND NOT tgisinternal
                """
            )
        ).fetchone()
        self.assertEqual(triggers, (0,))
        objects = await (
            await self.connection.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = %s ORDER BY table_name
                """,
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(objects, [("material_stock",)])
        routines = await (
            await self.connection.execute(
                "SELECT routine_name FROM information_schema.routines "
                "WHERE routine_schema = %s",
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(routines, [])
        dependencies = await (
            await self.connection.execute(
                """
                SELECT count(*)
                FROM pg_depend d
                JOIN pg_class source ON source.oid = d.objid
                JOIN pg_class target ON target.oid = d.refobjid
                WHERE source.oid = 'material_stock'::regclass
                  AND target.relname = 'registry_records'
                """
            )
        ).fetchone()
        self.assertEqual(dependencies, (0,))
        after_roles = await (
            await self.connection.execute("SELECT rolname FROM pg_roles ORDER BY rolname")
        ).fetchall()
        self.assertEqual(after_roles, before_roles)
        grants = await (
            await self.connection.execute(
                """
                SELECT grantee, privilege_type FROM information_schema.role_table_grants
                WHERE table_schema = %s AND table_name = 'material_stock'
                  AND grantee <> current_user
                """,
                (self.schema,),
            )
        ).fetchall()
        self.assertEqual(grants, [])
        count = await (
            await self.connection.execute("SELECT count(*) FROM material_stock")
        ).fetchone()
        self.assertEqual(count, (0,))

    async def test_value_constraints_defaults_and_duplicate_key(self):
        await self.connection.execute(UP)
        fixed_id = uuid.uuid4()
        await self._insert(material_id=fixed_id, name="Same name")
        await self._insert(name="Same name")
        with self.assertRaises(psycopg.errors.UniqueViolation):
            await self._insert(material_id=fixed_id)

        for missing in (
            "material_id",
            "name",
            "stock_qty",
            "unit",
            "is_active",
            "updated_at",
        ):
            with self.subTest(missing=missing):
                values = {
                    "material_id": uuid.uuid4(),
                    "name": "Required fields",
                    "stock_qty": Decimal("1"),
                    "unit": "pcs",
                    "is_active": True,
                    "updated_at": datetime.now(timezone.utc),
                }
                del values[missing]
                columns = sql.SQL(", ").join(map(sql.Identifier, values))
                placeholders = sql.SQL(", ").join(sql.Placeholder(key) for key in values)
                with self.assertRaises(psycopg.errors.NotNullViolation):
                    await self.connection.execute(
                        sql.SQL("INSERT INTO material_stock ({}) VALUES ({})").format(
                            columns, placeholders
                        ),
                        values,
                    )

        for invalid_name in ("", "   "):
            with self.subTest(name=repr(invalid_name)):
                with self.assertRaises(psycopg.errors.CheckViolation):
                    await self._insert(name=invalid_name)
        for quantity in (Decimal("0"), Decimal("7"), Decimal("3.125678")):
            with self.subTest(quantity=quantity):
                await self._insert(stock_qty=quantity)
        with self.assertRaises(psycopg.errors.CheckViolation):
            await self._insert(stock_qty=Decimal("-0.000001"))
        for unit in ("sheet", "pcs", "kg", "roll", "pack"):
            with self.subTest(unit=unit):
                await self._insert(unit=unit)
        for unit in ("unknown", "SHEET"):
            with self.subTest(unit=unit):
                with self.assertRaises(psycopg.errors.CheckViolation):
                    await self._insert(unit=unit)
        await self._insert(is_active=True)
        await self._insert(is_active=False)

    async def test_governed_down_preserves_unrelated_object_and_reapply(self):
        await self.connection.execute("CREATE TABLE unrelated_guard (id INTEGER PRIMARY KEY)")
        await self.connection.execute("INSERT INTO unrelated_guard VALUES (1)")
        await self.connection.execute(UP)
        await self.connection.execute(DOWN)
        self.assertEqual(
            await (
                await self.connection.execute("SELECT to_regclass('material_stock')")
            ).fetchone(),
            (None,),
        )
        self.assertEqual(
            await (
                await self.connection.execute("SELECT * FROM unrelated_guard")
            ).fetchall(),
            [(1,)],
        )
        await self.connection.execute(UP)
        self.assertEqual(
            await (
                await self.connection.execute("SELECT to_regclass('material_stock')")
            ).fetchone(),
            ("material_stock",),
        )


if __name__ == "__main__":
    unittest.main()
