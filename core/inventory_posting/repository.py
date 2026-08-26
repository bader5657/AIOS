"""Authoritative, transactional Psycopg inventory posting boundary."""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg import conninfo

from .errors import InventoryPostingError, InventoryPostingFailureCode as Code
from .models import (
    IdempotencyOutcome,
    MovementEvidence,
    PostingOutcome,
    PostingResult,
)


class InventoryPostingRepository:
    """Expose only one governed posting operation over posting credentials."""

    def __init__(
        self,
        database_url: str,
        *,
        movement_id_factory: Callable[[], UUID] = uuid.uuid4,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        if not isinstance(database_url, str) or not database_url:
            raise ValueError("database_url must be non-blank text")
        if not callable(movement_id_factory) or not callable(clock):
            raise ValueError("identity and clock sources must be callable")
        self._database_url = database_url
        self._movement_id_factory = movement_id_factory
        self._clock = clock

    @classmethod
    def from_environment(cls) -> "InventoryPostingRepository":
        password = os.environ.get("AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD")
        if not password:
            raise ValueError(
                "AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD is required"
            )
        return cls(
            conninfo.make_conninfo(
                host="127.0.0.1",
                port=5432,
                dbname="aios",
                user="aios_material_inventory_posting_runtime",
                password=password,
                sslmode="disable",
            )
        )

    async def post_confirmed_receipt(
        self, receipt_id: UUID, expected_version: int, actor_reference: str
    ) -> PostingResult:
        if type(receipt_id) is not UUID:
            raise ValueError("receipt_id must be a UUID")
        if type(expected_version) is not int or expected_version <= 0:
            raise ValueError("expected_version must be positive")
        if not isinstance(actor_reference, str) or not actor_reference.strip():
            raise ValueError("actor_reference must be non-blank text")
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    await con.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                    receipt = await (
                        await con.execute(
                            "SELECT status, version, confirmed_version FROM "
                            "material_receipts WHERE receipt_id = %s FOR UPDATE",
                            (receipt_id,),
                        )
                    ).fetchone()
                    if receipt is None:
                        raise InventoryPostingError(Code.RECEIPT_NOT_FOUND)
                    status, version, confirmed_version = receipt
                    if version != expected_version:
                        raise InventoryPostingError(Code.STALE_RECEIPT_VERSION)
                    if status == "POSTED":
                        return await self._already_posted(
                            con, receipt_id, version, actor_reference
                        )
                    if status != "CONFIRMED":
                        raise InventoryPostingError(Code.INVALID_RECEIPT_STATE)
                    if confirmed_version != version:
                        raise InventoryPostingError(Code.RECEIPT_NOT_CONFIRMED)
                    items = await (
                        await con.execute(
                            """
                            SELECT receipt_item_id, material_id, line_number,
                                   full_colly_count, qty_per_full_colly,
                                   partial_qty, total_qty, unit, status
                            FROM material_receipt_items
                            WHERE receipt_id = %s AND status = 'CONFIRMED'
                            ORDER BY material_id, line_number, receipt_item_id
                            FOR UPDATE
                            """,
                            (receipt_id,),
                        )
                    ).fetchall()
                    if not items:
                        raise InventoryPostingError(Code.NO_POSTABLE_ITEMS)
                    for item in items:
                        self._validate_item(item)
                    existing = await (
                        await con.execute(
                            """
                            SELECT movement_id, source_receipt_item_id, material_id,
                                   quantity_delta, unit, balance_before, balance_after
                            FROM inventory_movements
                            WHERE source_receipt_item_id = ANY(%s)
                            ORDER BY source_receipt_item_id
                            """,
                            ([item[0] for item in items],),
                        )
                    ).fetchall()
                    if existing:
                        raise InventoryPostingError(Code.CONFLICTING_POSTING)
                    material_ids = sorted({item[1] for item in items}, key=str)
                    materials = await (
                        await con.execute(
                            "SELECT material_id, stock_qty, unit, is_active FROM "
                            "material_stock WHERE material_id = ANY(%s) "
                            "ORDER BY material_id FOR UPDATE",
                            (material_ids,),
                        )
                    ).fetchall()
                    material_map = {row[0]: row for row in materials}
                    for item in items:
                        material = material_map.get(item[1])
                        if material is None:
                            raise InventoryPostingError(Code.MATERIAL_NOT_FOUND)
                        if not material[3]:
                            raise InventoryPostingError(Code.MATERIAL_INACTIVE)
                        if item[7] != material[2]:
                            raise InventoryPostingError(Code.UNIT_MISMATCH)
                    balances = {row[0]: row[1] for row in materials}
                    occurred_at = self._clock()
                    evidence: list[MovementEvidence] = []
                    for item in items:
                        item_id, material_id, _, _, _, _, total, unit, _ = item
                        before = balances[material_id]
                        after = before + total
                        movement_id = self._movement_id_factory()
                        await con.execute(
                            """
                            INSERT INTO inventory_movements (
                                movement_id, material_id, movement_type,
                                quantity_delta, unit, source_receipt_item_id,
                                occurred_at, posting_actor_reference,
                                balance_before, balance_after
                            ) VALUES (%s, %s, 'RECEIPT', %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                movement_id, material_id, total, unit, item_id,
                                occurred_at, actor_reference, before, after,
                            ),
                        )
                        returned = await (
                            await con.execute(
                                "UPDATE material_stock SET stock_qty = stock_qty + %s, "
                                "updated_at = %s WHERE material_id = %s "
                                "RETURNING stock_qty",
                                (total, occurred_at, material_id),
                            )
                        ).fetchone()
                        if returned is None or returned[0] != after:
                            raise InventoryPostingError(Code.DATA_INTEGRITY_ERROR)
                        balances[material_id] = returned[0]
                        evidence.append(
                            MovementEvidence(
                                movement_id, item_id, material_id, total, unit,
                                before, returned[0],
                            )
                        )
                    item_ids = [item[0] for item in items]
                    updated = await (
                        await con.execute(
                            "UPDATE material_receipt_items SET status = 'POSTED', "
                            "updated_at = %s WHERE receipt_item_id = ANY(%s) "
                            "AND status = 'CONFIRMED' RETURNING receipt_item_id",
                            (occurred_at, item_ids),
                        )
                    ).fetchall()
                    if len(updated) != len(items):
                        raise InventoryPostingError(Code.ITEM_NOT_CONFIRMED)
                    receipt_updated = await (
                        await con.execute(
                            "UPDATE material_receipts SET status = 'POSTED', "
                            "updated_at = %s WHERE receipt_id = %s AND status = "
                            "'CONFIRMED' RETURNING receipt_id",
                            (occurred_at, receipt_id),
                        )
                    ).fetchone()
                    if receipt_updated is None:
                        raise InventoryPostingError(Code.INVALID_RECEIPT_STATE)
                    return PostingResult(
                        receipt_id, version, actor_reference, PostingOutcome.POSTED,
                        IdempotencyOutcome.CREATED, occurred_at, tuple(evidence),
                    )
        except InventoryPostingError:
            raise
        except psycopg.OperationalError as exc:
            raise InventoryPostingError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.errors.UniqueViolation as exc:
            raise InventoryPostingError(Code.CONFLICTING_POSTING) from exc
        except psycopg.Error as exc:
            raise InventoryPostingError(Code.DATA_INTEGRITY_ERROR) from exc

    @staticmethod
    def _validate_item(item: tuple[object, ...]) -> None:
        _, material_id, _, full, per_colly, partial, total, unit, status = item
        if status != "CONFIRMED":
            raise InventoryPostingError(Code.ITEM_NOT_CONFIRMED)
        if material_id is None:
            raise InventoryPostingError(Code.MATERIAL_UNRESOLVED)
        calculated = Decimal(full) * (per_colly or Decimal(0)) + partial
        if total != calculated or total <= 0:
            raise InventoryPostingError(Code.PACKAGING_FORMULA_INVALID)
        if unit == "sheet" and any(
            value is not None and value != value.to_integral_value()
            for value in (per_colly, partial, total)
        ):
            raise InventoryPostingError(Code.PACKAGING_FORMULA_INVALID)

    async def _already_posted(
        self, con: psycopg.AsyncConnection, receipt_id: UUID, version: int,
        actor_reference: str,
    ) -> PostingResult:
        rows = await (
            await con.execute(
                """
                SELECT m.movement_id, m.source_receipt_item_id, m.material_id,
                       m.quantity_delta, m.unit, m.balance_before, m.balance_after,
                       m.posted_at, i.material_id, i.total_qty, i.unit, i.status
                FROM material_receipt_items i
                LEFT JOIN inventory_movements m
                  ON m.source_receipt_item_id = i.receipt_item_id
                WHERE i.receipt_id = %s
                  AND i.status NOT IN ('CANCELLED', 'REJECTED')
                ORDER BY i.material_id, i.line_number, i.receipt_item_id
                """,
                (receipt_id,),
            )
        ).fetchall()
        if not rows:
            raise InventoryPostingError(Code.CONFLICTING_POSTING)
        evidence = []
        posted_at = None
        for row in rows:
            if (
                row[11] != "POSTED"
                or row[0] is None
                or row[2] != row[8]
                or row[3] != row[9]
                or row[4] != row[10]
            ):
                raise InventoryPostingError(Code.CONFLICTING_POSTING)
            if row[6] != row[5] + row[3]:
                raise InventoryPostingError(Code.CONFLICTING_POSTING)
            posted_at = row[7] if posted_at is None else max(posted_at, row[7])
            evidence.append(MovementEvidence(*row[:7]))
        return PostingResult(
            receipt_id, version, actor_reference, PostingOutcome.ALREADY_POSTED,
            IdempotencyOutcome.REPLAYED, posted_at, tuple(evidence),
        )
