"""Permanent disposable PostgreSQL proof for Stage 0.33A."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import unittest
import uuid

import psycopg

from tests.integration.business_context.disposable_postgres import OPT_IN, admit_disposable_postgres


ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS = ROOT / "migrations/postgres"
STOCK_UP = (MIGRATIONS / "0002_create_material_stock.up.sql").read_text()
STOCK_DOWN = (MIGRATIONS / "0002_create_material_stock.down.sql").read_text()
RECEIPT_UP = (MIGRATIONS / "0003_create_material_receipt_inventory_movement.up.sql").read_text()
RECEIPT_DOWN = (MIGRATIONS / "0003_create_material_receipt_inventory_movement.down.sql").read_text()
STAGE032_UP = (MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.up.sql").read_text()
STAGE032_DOWN = (MIGRATIONS / "0004_add_material_receipt_source_active_uniqueness.down.sql").read_text()
UP = (MIGRATIONS / "0005_add_material_receipt_creator_provenance.up.sql").read_text()
DOWN = (MIGRATIONS / "0005_add_material_receipt_creator_provenance.down.sql").read_text()
ROLE = "aios_material_receipt_candidate_writer"
CONSTRAINT = "material_receipts_created_by_actor_reference_valid"
INDEX = "material_receipts_source_asset_active_uidx"
VALID = "operator:550e8400-e29b-41d4-a716-446655440000"
TEST_URL = os.environ.get("AIOS_MATERIAL_TEST_DATABASE_URL")


async def catalog_snapshot(db) -> dict[str, tuple[tuple[object, ...], ...]]:
    queries = {
        "columns": """SELECT table_name,column_name,ordinal_position,data_type,
            is_nullable,column_default FROM information_schema.columns
            WHERE table_schema='public' ORDER BY table_name,ordinal_position""",
        "constraints": """SELECT relation.relname,constraint_.conname,
            constraint_.contype,pg_get_constraintdef(constraint_.oid)
            FROM pg_constraint constraint_
            JOIN pg_class relation ON relation.oid=constraint_.conrelid
            JOIN pg_namespace namespace ON namespace.oid=relation.relnamespace
            WHERE namespace.nspname='public'
            ORDER BY relation.relname,constraint_.conname""",
        "indexes": """SELECT relation.relname,index_.relname,definition.indisunique,
            definition.indisvalid,definition.indisready,
            pg_get_indexdef(definition.indexrelid),
            pg_get_expr(definition.indpred,definition.indrelid)
            FROM pg_index definition
            JOIN pg_class relation ON relation.oid=definition.indrelid
            JOIN pg_class index_ ON index_.oid=definition.indexrelid
            JOIN pg_namespace namespace ON namespace.oid=relation.relnamespace
            WHERE namespace.nspname='public' ORDER BY relation.relname,index_.relname""",
        "triggers": """SELECT relation.relname,trigger_.tgname,
            pg_get_triggerdef(trigger_.oid) FROM pg_trigger trigger_
            JOIN pg_class relation ON relation.oid=trigger_.tgrelid
            JOIN pg_namespace namespace ON namespace.oid=relation.relnamespace
            WHERE namespace.nspname='public' AND NOT trigger_.tgisinternal
            ORDER BY relation.relname,trigger_.tgname""",
        "functions": """SELECT procedure.proname,
            pg_get_function_identity_arguments(procedure.oid),
            pg_get_functiondef(procedure.oid),owner.rolname
            FROM pg_proc procedure
            JOIN pg_namespace namespace ON namespace.oid=procedure.pronamespace
            JOIN pg_roles owner ON owner.oid=procedure.proowner
            WHERE namespace.nspname='public'
            ORDER BY procedure.proname,pg_get_function_identity_arguments(procedure.oid)""",
        "owners": """SELECT 'database',current_database(),owner.rolname
            FROM pg_database database_ JOIN pg_roles owner ON owner.oid=database_.datdba
            WHERE database_.datname=current_database()
            UNION ALL SELECT 'schema',namespace.nspname,owner.rolname
            FROM pg_namespace namespace JOIN pg_roles owner ON owner.oid=namespace.nspowner
            WHERE namespace.nspname='public'
            UNION ALL SELECT 'relation',relation.relname,owner.rolname
            FROM pg_class relation
            JOIN pg_namespace namespace ON namespace.oid=relation.relnamespace
            JOIN pg_roles owner ON owner.oid=relation.relowner
            WHERE namespace.nspname='public' AND relation.relkind IN ('r','p','S','v','m','f')
            ORDER BY 1,2""",
        "roles": """SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,
            rolcanlogin,rolreplication,rolbypassrls
            FROM pg_roles ORDER BY rolname""",
        "memberships": """SELECT granted.rolname,member.rolname,membership.admin_option
            FROM pg_auth_members membership
            JOIN pg_roles granted ON granted.oid=membership.roleid
            JOIN pg_roles member ON member.oid=membership.member
            ORDER BY granted.rolname,member.rolname""",
        "table_privileges": """SELECT table_name,grantee,privilege_type,is_grantable
            FROM information_schema.table_privileges WHERE table_schema='public'
            ORDER BY table_name,grantee,privilege_type,is_grantable""",
        "column_privileges": """SELECT table_name,column_name,grantee,
            privilege_type,is_grantable FROM information_schema.column_privileges
            WHERE table_schema='public' AND grantee <> current_user
            ORDER BY table_name,column_name,grantee,privilege_type,is_grantable""",
        "relations": """SELECT relation.relname,relation.relkind
            FROM pg_class relation JOIN pg_namespace namespace
            ON namespace.oid=relation.relnamespace WHERE namespace.nspname='public'
            ORDER BY relation.relname,relation.relkind""",
        "business_data": """SELECT 'material_stock',count(*),
            COALESCE(sum(stock_qty),0)::text FROM public.material_stock""",
    }
    result = {}
    for name, query in queries.items():
        result[name] = tuple(await (await db.execute(query)).fetchall())
    return result


@unittest.skipUnless(TEST_URL or os.environ.get(OPT_IN), "disposable PostgreSQL configuration is required")
class Stage033AProvenancePostgresTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.target = admit_disposable_postgres(TEST_URL)
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(f"CREATE ROLE {ROLE} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS")
            await db.execute(STOCK_UP)
            await db.execute(RECEIPT_UP)
            await db.execute(STAGE032_UP)
            await db.execute(
                "INSERT INTO public.material_stock "
                "(material_id,name,stock_qty,unit,is_active,updated_at) "
                "VALUES (%s,'Stage 033A preservation fixture',7,'sheet',true,%s)",
                (uuid.uuid4(), datetime.now(timezone.utc)),
            )
            self.before_catalog = await catalog_snapshot(db)
            self.before_indexes = tuple(await (await db.execute("SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname")).fetchall())
            self.before_roles = tuple(await (await db.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolcanlogin FROM pg_roles ORDER BY rolname")).fetchall())
            await db.execute(UP)
            self.after_catalog = await catalog_snapshot(db)

    async def asyncTearDown(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            exists = (await (await db.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='material_receipts' AND column_name='created_by_actor_reference'")).fetchone())
            if exists:
                await db.execute(DOWN)
            await db.execute(STAGE032_DOWN)
            await db.execute(RECEIPT_DOWN)
            await db.execute(STOCK_DOWN)
            await db.execute(f"DROP ROLE {ROLE}")

    async def insert(self, actor) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute("INSERT INTO public.material_receipts(receipt_id,supplier_name,received_at,source_asset_reference,created_by_actor_reference) VALUES(%s,'Stage 033A',%s,%s,%s)", (uuid.uuid4(), datetime.now(timezone.utc), "asset:" + uuid.uuid4().hex, actor))

    async def test_up_schema_constraint_grant_and_preservation_are_exact(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url) as db:
            column = await (await db.execute("SELECT data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='material_receipts' AND column_name='created_by_actor_reference'")).fetchone()
            constraint = await (await db.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='public.material_receipts'::regclass AND conname=%s", (CONSTRAINT,))).fetchone()
            indexes = tuple(await (await db.execute("SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY indexname")).fetchall())
            roles = tuple(await (await db.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolcanlogin FROM pg_roles ORDER BY rolname")).fetchall())
            grant = await (await db.execute("SELECT has_column_privilege(%s,'public.material_receipts','created_by_actor_reference','INSERT'),has_column_privilege(%s,'public.material_receipts','created_by_actor_reference','UPDATE')", (ROLE, ROLE))).fetchone()
        self.assertEqual(column, ("text", "NO", None))
        self.assertIn("operator:", constraint[0]); self.assertIn("4[0-9a-f]", constraint[0]); self.assertIn("[89ab]", constraint[0])
        self.assertEqual(indexes, self.before_indexes); self.assertEqual(roles, self.before_roles)
        self.assertEqual(grant, (True, False)); self.assertTrue(any(name == INDEX for name, _ in indexes))

    async def test_complete_catalog_and_business_data_preservation(self) -> None:
        unchanged = {
            "indexes", "triggers", "functions", "owners", "roles", "memberships",
            "table_privileges", "relations", "business_data",
        }
        for name in unchanged:
            with self.subTest(catalog=name):
                self.assertEqual(self.after_catalog[name], self.before_catalog[name])

        added_columns = set(self.after_catalog["columns"]) - set(self.before_catalog["columns"])
        removed_columns = set(self.before_catalog["columns"]) - set(self.after_catalog["columns"])
        self.assertEqual(removed_columns, set())
        self.assertEqual(len(added_columns), 1)
        added_column = next(iter(added_columns))
        self.assertEqual(added_column[0:2], ("material_receipts", "created_by_actor_reference"))
        self.assertEqual(added_column[3:], ("text", "NO", None))

        added_constraints = (
            set(self.after_catalog["constraints"]) - set(self.before_catalog["constraints"])
        )
        self.assertEqual(len(added_constraints), 1)
        added_constraint = next(iter(added_constraints))
        self.assertEqual(added_constraint[:3], ("material_receipts", CONSTRAINT, "c"))
        self.assertIn("4[0-9a-f]", added_constraint[3])
        self.assertIn("[89ab]", added_constraint[3])
        self.assertEqual(
            set(self.before_catalog["constraints"]) - set(self.after_catalog["constraints"]),
            set(),
        )

        added_column_grants = (
            set(self.after_catalog["column_privileges"])
            - set(self.before_catalog["column_privileges"])
        )
        self.assertEqual(
            added_column_grants,
            {("material_receipts", "created_by_actor_reference", ROLE, "INSERT", "NO")},
        )
        self.assertEqual(
            set(self.before_catalog["column_privileges"])
            - set(self.after_catalog["column_privileges"]),
            set(),
        )

        source_index = [
            row for row in self.after_catalog["indexes"] if row[1] == INDEX
        ]
        self.assertEqual(len(source_index), 1)
        self.assertEqual(source_index[0][2:5], (True, True, True))
        self.assertIn("(source_asset_reference)", source_index[0][5])
        self.assertEqual(source_index[0][6], "(status <> ALL (ARRAY['REJECTED'::text, 'CANCELLED'::text]))")

    async def test_database_check_accepts_only_canonical_operator_uuidv4(self) -> None:
        await self.insert(VALID)
        rejected = [
            None, "", VALID.upper(), "operator:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "operator:9073926b-929f-31c2-abc9-fad77ae3e8eb",
            "operator:4d73d0f2-68c3-5c4c-8d58-7f97e9275c8d",
            "operator:00000000-0000-0000-0000-000000000000",
            "operator:550e8400-e29b-41d4-7716-446655440000", "operator:not-a-uuid",
            "operator:550e8400e29b41d4a716446655440000", "operator:{550e8400-e29b-41d4-a716-446655440000}",
            " " + VALID, VALID + " ", VALID.replace("operator:", "reviewer:"), VALID.replace("operator:", "system:"),
        ]
        for actor in rejected:
            with self.subTest(actor=actor), self.assertRaises((psycopg.errors.CheckViolation, psycopg.errors.NotNullViolation)):
                await self.insert(actor)

    async def test_conditional_bootstrap_creator_grant_is_safe_and_idempotent(self) -> None:
        conditional_grant = f"""
        DO $grant_creator$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='material_receipts'
              AND column_name='created_by_actor_reference'
          ) THEN
            GRANT INSERT (created_by_actor_reference)
              ON public.material_receipts TO {ROLE};
          END IF;
        END $grant_creator$;
        """
        async with await psycopg.AsyncConnection.connect(
            self.target.url, autocommit=True
        ) as db:
            await db.execute(DOWN)
            before_grants = tuple(await (await db.execute(
                "SELECT table_name,column_name,grantee,privilege_type,is_grantable "
                "FROM information_schema.column_privileges "
                "WHERE table_schema='public' AND grantee=%s "
                "ORDER BY table_name,column_name,privilege_type",
                (ROLE,),
            )).fetchall())
            await db.execute(conditional_grant)
            await db.execute(conditional_grant)
            grants_before_migration = tuple(await (await db.execute(
                "SELECT table_name,column_name,grantee,privilege_type,is_grantable "
                "FROM information_schema.column_privileges "
                "WHERE table_schema='public' AND grantee=%s "
                "ORDER BY table_name,column_name,privilege_type",
                (ROLE,),
            )).fetchall())
            self.assertEqual(grants_before_migration, before_grants)

            await db.execute(UP)
            await db.execute(conditional_grant)
            await db.execute(conditional_grant)
            effective = await (await db.execute(
                "SELECT has_column_privilege(%s,'public.material_receipts',"
                "'created_by_actor_reference','INSERT'),"
                "has_column_privilege(%s,'public.material_receipts',"
                "'created_by_actor_reference','UPDATE'),"
                "has_table_privilege(%s,'public.material_receipts','INSERT'),"
                "has_table_privilege(%s,'public.material_receipts','UPDATE')",
                (ROLE, ROLE, ROLE, ROLE),
            )).fetchone()
            self.assertEqual(effective, (True, False, False, False))
            creator_acl = tuple(await (await db.execute(
                "SELECT privilege_type,is_grantable FROM information_schema.column_privileges "
                "WHERE table_schema='public' AND table_name='material_receipts' "
                "AND column_name='created_by_actor_reference' AND grantee=%s",
                (ROLE,),
            )).fetchall())
            self.assertEqual(creator_acl, (("INSERT", "NO"),))

            await db.execute(DOWN)
            after_down = tuple(await (await db.execute(
                "SELECT table_name,column_name,grantee,privilege_type,is_grantable "
                "FROM information_schema.column_privileges "
                "WHERE table_schema='public' AND grantee=%s "
                "ORDER BY table_name,column_name,privilege_type",
                (ROLE,),
            )).fetchall())
            self.assertEqual(after_down, before_grants)
            await db.execute(UP)

    async def test_down_and_up_lifecycle_is_disposable_and_exact(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.target.url, autocommit=True) as db:
            await db.execute(DOWN)
            column = await (await db.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='material_receipts' AND column_name='created_by_actor_reference'")).fetchone()
            self.assertIsNone(column)
            self.assertTrue((await (await db.execute("SELECT to_regclass('public.material_receipts_source_asset_active_uidx')")).fetchone())[0])
            await db.execute(UP)
        await self.insert(VALID)


if __name__ == "__main__":
    unittest.main()
