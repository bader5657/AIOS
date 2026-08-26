from datetime import datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
import unittest
import uuid

import psycopg
from psycopg import conninfo, sql

from core.inventory_posting import (
    InventoryPostingError, InventoryPostingFailureCode as Code,
    InventoryPostingRepository, PostingOutcome,
)
from core.inventory_posting.repository import PostingDatabaseConfig
from tests.integration.business_context.disposable_postgres import (
    OPT_IN,
    admit_disposable_postgres,
)


TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
STOCK_SQL = (ROOT / "migrations/postgres/0002_create_material_stock.up.sql").read_text()
RECEIPT_SQL = (ROOT / "migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql").read_text()


@unittest.skipUnless(
    TEST_URL or os.environ.get(OPT_IN),
    "disposable PostgreSQL configuration is required",
)
class PostingRepositoryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.target = admit_disposable_postgres(TEST_URL)
        self.schema = "posting_" + uuid.uuid4().hex
        self.runtime_user = "aios_material_inventory_posting_runtime"
        self.runtime_password = "posting-disposable-only"
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(self.runtime_user),
                    sql.Literal(self.runtime_password),
                )
            )
            await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.url = conninfo.make_conninfo(
            self.target.url, options=f"-csearch_path={self.schema}"
        )
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(STOCK_SQL)
            await con.execute(RECEIPT_SQL)
            role = sql.Identifier(self.runtime_user)
            schema = sql.Identifier(self.schema)
            await con.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role)
            )
            await con.execute(sql.SQL(
                "GRANT SELECT ON material_receipts,material_receipt_items,"
                "inventory_movements,material_stock TO {}"
            ).format(role))
            await con.execute(sql.SQL(
                "GRANT UPDATE (status,updated_at) ON material_receipts,"
                "material_receipt_items TO {}"
            ).format(role))
            await con.execute(sql.SQL(
                "GRANT INSERT (movement_id,material_id,movement_type,quantity_delta,"
                "unit,source_receipt_item_id,occurred_at,posting_actor_reference,"
                "balance_before,balance_after) ON inventory_movements TO {}"
            ).format(role))
            await con.execute(sql.SQL(
                "GRANT UPDATE (stock_qty,updated_at) ON material_stock TO {}"
            ).format(role))
        self.repository = InventoryPostingRepository(
            PostingDatabaseConfig(
                password=self.runtime_password,
                host=self.target.host,
                port=self.target.port,
                dbname=self.target.dbname,
                search_path=self.schema,
            )
        )

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as admin:
            await admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema)))
            await admin.execute(
                sql.SQL("DROP ROLE {}").format(sql.Identifier(self.runtime_user))
            )

    async def material(self, stock="1000", unit="sheet", active=True):
        material_id = uuid.uuid4()
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(
                "INSERT INTO material_stock VALUES (%s,%s,%s,%s,%s,%s)",
                (material_id, "EF", Decimal(stock), unit, active,
                 datetime.now(timezone.utc)),
            )
        return material_id

    async def confirmed_receipt(self, lines, *, status="CONFIRMED", version=1):
        receipt_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(
                """
                INSERT INTO material_receipts (
                    receipt_id,supplier_name,received_at,source_asset_reference,
                    status,version,confirmed_version,confirmed_at,
                    confirmation_actor_reference
                ) VALUES (%s,'Supplier',%s,'asset:test',%s,%s,%s,%s,'operator:confirm')
                """,
                (receipt_id, now, status, version,
                 version if status in {"CONFIRMED", "POSTED"} else None,
                 now if status in {"CONFIRMED", "POSTED"} else None),
            )
            item_ids = []
            for index, line in enumerate(lines, 1):
                item_id = uuid.uuid4(); item_ids.append(item_id)
                await con.execute(
                    """
                    INSERT INTO material_receipt_items (
                        receipt_item_id,receipt_id,line_number,material_id,
                        full_colly_count,qty_per_full_colly,partial_qty,total_qty,
                        unit,status
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (item_id, receipt_id, index, line[0], line[1], line[2],
                     line[3], line[4], line[5], line[6] if len(line) > 6 else "CONFIRMED"),
                )
        return receipt_id, item_ids

    async def stock(self, material_id):
        async with await psycopg.AsyncConnection.connect(self.url) as con:
            return (await (await con.execute(
                "SELECT stock_qty FROM material_stock WHERE material_id=%s",
                (material_id,),
            )).fetchone())[0]

    async def test_single_item_exact_balance_and_retry(self):
        material = await self.material()
        receipt, items = await self.confirmed_receipt([
            (material, 125, Decimal("50"), Decimal("0"), Decimal("6250"), "sheet")
        ])
        posted = await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(posted.outcome, PostingOutcome.POSTED)
        self.assertEqual(posted.movements[0].balance_before, Decimal("1000"))
        self.assertEqual(posted.movements[0].balance_after, Decimal("7250"))
        self.assertEqual(await self.stock(material), Decimal("7250"))
        replay = await self.repository.post_confirmed_receipt(receipt, 1, "operator:retry")
        self.assertEqual(replay.outcome, PostingOutcome.ALREADY_POSTED)
        self.assertEqual(await self.stock(material), Decimal("7250"))
        self.assertEqual(replay.movements[0].source_receipt_item_id, items[0])

    async def test_multi_item_same_material_is_sequential_and_per_line(self):
        material = await self.material()
        receipt, _ = await self.confirmed_receipt([
            (material,125,Decimal("50"),Decimal("0"),Decimal("6250"),"sheet"),
            (material,62,Decimal("50"),Decimal("38"),Decimal("3138"),"sheet"),
        ])
        result = await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual([(m.balance_before, m.balance_after) for m in result.movements], [
            (Decimal("1000"), Decimal("7250")),
            (Decimal("7250"), Decimal("10388")),
        ])
        self.assertEqual(await self.stock(material), Decimal("10388"))
        self.assertEqual(len({m.movement_id for m in result.movements}), 2)

    async def test_multi_material_deterministic_order(self):
        first, second = sorted([await self.material(), await self.material()], key=str)
        receipt, _ = await self.confirmed_receipt([
            (second,1,Decimal("10"),Decimal("0"),Decimal("10"),"sheet"),
            (first,1,Decimal("20"),Decimal("0"),Decimal("20"),"sheet"),
        ])
        result = await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual([m.material_id for m in result.movements], [first, second])

    async def test_validation_failure_rolls_back_all_lifecycle_and_stock(self):
        good = await self.material()
        inactive = await self.material(active=False)
        receipt, item_ids = await self.confirmed_receipt([
            (good,1,Decimal("50"),Decimal("0"),Decimal("50"),"sheet"),
            (inactive,1,Decimal("50"),Decimal("0"),Decimal("50"),"sheet"),
        ])
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.MATERIAL_INACTIVE)
        self.assertEqual(await self.stock(good), Decimal("1000"))
        async with await psycopg.AsyncConnection.connect(self.url) as con:
            movement_count = (await (await con.execute(
                "SELECT count(*) FROM inventory_movements"
            )).fetchone())[0]
            states = await (await con.execute(
                "SELECT status FROM material_receipt_items WHERE receipt_id=%s ORDER BY line_number",
                (receipt,),
            )).fetchall()
            receipt_state = (await (await con.execute(
                "SELECT status FROM material_receipts WHERE receipt_id=%s", (receipt,)
            )).fetchone())[0]
        self.assertEqual(movement_count, 0)
        self.assertEqual(states, [("CONFIRMED",), ("CONFIRMED",)])
        self.assertEqual(receipt_state, "CONFIRMED")

    async def test_later_stock_failure_rolls_back_first_item_effects(self):
        first, second = sorted([await self.material(), await self.material()], key=str)
        receipt, _ = await self.confirmed_receipt([
            (first,1,Decimal("10"),Decimal("0"),Decimal("10"),"sheet"),
            (second,1,Decimal("20"),Decimal("0"),Decimal("20"),"sheet"),
        ])
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(
                """
                CREATE FUNCTION fail_second_stock() RETURNS trigger LANGUAGE plpgsql AS $$
                BEGIN
                    IF NEW.material_id = '%s'::uuid THEN
                        RAISE EXCEPTION 'disposable later-item failure';
                    END IF;
                    RETURN NEW;
                END $$
                """ % second
            )
            await con.execute(
                "CREATE TRIGGER fail_second_stock BEFORE UPDATE ON material_stock "
                "FOR EACH ROW EXECUTE FUNCTION fail_second_stock()"
            )
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.DATA_INTEGRITY_ERROR)
        self.assertEqual(await self.stock(first), Decimal("1000"))
        self.assertEqual(await self.stock(second), Decimal("1000"))
        async with await psycopg.AsyncConnection.connect(self.url) as con:
            count = (await (await con.execute(
                "SELECT count(*) FROM inventory_movements"
            )).fetchone())[0]
            states = await (await con.execute(
                "SELECT status FROM material_receipt_items WHERE receipt_id=%s",
                (receipt,),
            )).fetchall()
        self.assertEqual(count, 0)
        self.assertEqual(states, [("CONFIRMED",), ("CONFIRMED",)])

    async def test_cancelled_item_is_ignored(self):
        material = await self.material()
        receipt, _ = await self.confirmed_receipt([
            (material,1,Decimal("10"),Decimal("0"),Decimal("10"),"sheet"),
            (None,1,Decimal("10"),Decimal("0"),Decimal("10"),"sheet","CANCELLED"),
        ])
        result = await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(len(result.movements), 1)
        async with await psycopg.AsyncConnection.connect(self.url) as con:
            states = await (await con.execute(
                "SELECT status FROM material_receipt_items WHERE receipt_id=%s ORDER BY line_number",
                (receipt,),
            )).fetchall()
        self.assertEqual(states, [("POSTED",), ("CANCELLED",)])

    async def test_stale_invalid_state_and_no_postable_items(self):
        material = await self.material()
        receipt, _ = await self.confirmed_receipt([
            (material,1,Decimal("1"),Decimal("0"),Decimal("1"),"sheet")
        ])
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 2, "operator:post")
        self.assertEqual(caught.exception.code, Code.STALE_RECEIPT_VERSION)
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute("UPDATE material_receipts SET status='NEEDS_REVIEW', confirmed_version=NULL, confirmed_at=NULL, confirmation_actor_reference=NULL WHERE receipt_id=%s", (receipt,))
            await con.execute("UPDATE material_receipt_items SET status='NEEDS_REVIEW' WHERE receipt_id=%s", (receipt,))
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.INVALID_RECEIPT_STATE)

    async def test_conflicting_existing_movement_fails_closed(self):
        material = await self.material()
        receipt, item_ids = await self.confirmed_receipt([
            (material,1,Decimal("10"),Decimal("0"),Decimal("10"),"sheet")
        ])
        now = datetime.now(timezone.utc)
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute(
                "INSERT INTO inventory_movements (movement_id,material_id,movement_type,quantity_delta,unit,source_receipt_item_id,occurred_at,posting_actor_reference,balance_before,balance_after) VALUES (%s,%s,'RECEIPT',5,'sheet',%s,%s,'corrupt:test',1000,1005)",
                (uuid.uuid4(), material, item_ids[0], now),
            )
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.CONFLICTING_POSTING)
        self.assertEqual(await self.stock(material), Decimal("1000"))

    async def test_unit_mismatch_and_zero_applicable(self):
        kg = await self.material(unit="kg")
        receipt, _ = await self.confirmed_receipt([
            (kg,1,Decimal("1"),Decimal("0"),Decimal("1"),"sheet")
        ])
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.UNIT_MISMATCH)
        empty, _ = await self.confirmed_receipt([
            (None,1,Decimal("1"),Decimal("0"),Decimal("1"),"sheet","CANCELLED")
        ])
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(empty, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.NO_POSTABLE_ITEMS)

    async def test_missing_material_defense_fails_closed(self):
        material = await self.material()
        receipt, _ = await self.confirmed_receipt([
            (material,1,Decimal("1"),Decimal("0"),Decimal("1"),"sheet")
        ])
        async with await psycopg.AsyncConnection.connect(self.url, autocommit=True) as con:
            await con.execute("SET session_replication_role = replica")
            await con.execute("DELETE FROM material_stock WHERE material_id=%s", (material,))
            await con.execute("SET session_replication_role = origin")
        with self.assertRaises(InventoryPostingError) as caught:
            await self.repository.post_confirmed_receipt(receipt, 1, "operator:post")
        self.assertEqual(caught.exception.code, Code.MATERIAL_NOT_FOUND)

    async def test_movement_history_has_no_mutation_api(self):
        for name in ("update_movement", "delete_movement", "truncate_movements"):
            self.assertFalse(hasattr(self.repository, name))


if __name__ == "__main__":
    unittest.main()
