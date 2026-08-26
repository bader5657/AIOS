"""Explicit Psycopg persistence for material-receipt candidates."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Final
from uuid import UUID

import psycopg
from psycopg import conninfo

from .errors import MaterialReceiptError, MaterialReceiptFailureCode as Code
from .models import (
    ReceiptCandidateRequest,
    ReceiptDecision,
    ReceiptForReview,
    ReceiptItemCandidate,
    ReceiptItemView,
    ReceiptStatus,
)


_RECEIPT_COLUMNS: Final = (
    "receipt_id, supplier_name, document_number, document_date, received_at, "
    "source_asset_reference, status, version, confirmed_version, confirmed_at, "
    "confirmation_actor_reference"
)
_ITEM_COLUMNS: Final = (
    "receipt_item_id, line_number, candidate_material_description, "
    "canonical_display_name, size_description, specification, material_id, "
    "full_colly_count, qty_per_full_colly, partial_qty, total_qty, unit, status"
)


def _required_actor(actor_reference: object) -> str:
    if not isinstance(actor_reference, str) or not actor_reference.strip():
        raise ValueError("actor_reference must be non-blank text")
    return actor_reference


def _item_parameters(item: ReceiptItemCandidate) -> tuple[object, ...]:
    return (
        item.receipt_item_id,
        item.line_number,
        item.candidate_material_description,
        item.canonical_display_name,
        item.size_description,
        item.specification,
        item.material_id,
        item.full_colly_count,
        item.qty_per_full_colly,
        item.partial_qty,
        item.total_qty,
        item.unit,
    )


def _map_item(row: tuple[object, ...]) -> ReceiptItemView:
    return ReceiptItemView(*row[:-1], status=ReceiptStatus(row[-1]))


def _map_receipt(
    row: tuple[object, ...], items: tuple[ReceiptItemView, ...]
) -> ReceiptForReview:
    return ReceiptForReview(
        *row[:6],
        status=ReceiptStatus(row[6]),
        version=row[7],
        confirmed_version=row[8],
        confirmed_at=row[9],
        confirmation_actor_reference=row[10],
        items=items,
    )


class MaterialReceiptRepository:
    """Own one candidate-runtime connection and transaction per operation."""

    def __init__(self, database_url: str) -> None:
        if not isinstance(database_url, str) or not database_url:
            raise ValueError("database_url must be non-blank text")
        self._database_url = database_url

    @classmethod
    def from_environment(cls) -> "MaterialReceiptRepository":
        password = os.environ.get("AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD")
        if not password:
            raise ValueError(
                "AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD is required"
            )
        return cls(
            conninfo.make_conninfo(
                host="127.0.0.1",
                port=5432,
                dbname="aios",
                user="aios_material_receipt_candidate_runtime",
                password=password,
                sslmode="disable",
            )
        )

    async def create_receipt_candidate(
        self, request: ReceiptCandidateRequest
    ) -> ReceiptForReview:
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    await con.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                    await con.execute(
                        """
                        INSERT INTO material_receipts (
                            receipt_id, supplier_name, document_number, document_date,
                            received_at, source_asset_reference
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            request.receipt_id,
                            request.supplier_name,
                            request.document_number,
                            request.document_date,
                            request.received_at,
                            request.source_asset_reference,
                        ),
                    )
                    for item in request.items:
                        await self._insert_item(con, request.receipt_id, item)
                    now = datetime.now(timezone.utc)
                    await con.execute(
                        "UPDATE material_receipt_items SET status = 'NEEDS_REVIEW', "
                        "updated_at = %s WHERE receipt_id = %s",
                        (now, request.receipt_id),
                    )
                    await con.execute(
                        "UPDATE material_receipts SET status = 'NEEDS_REVIEW', "
                        "updated_at = %s WHERE receipt_id = %s",
                        (now, request.receipt_id),
                    )
                    return await self._read(con, request.receipt_id)
        except MaterialReceiptError:
            raise
        except psycopg.OperationalError as exc:
            raise MaterialReceiptError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.Error as exc:
            raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR) from exc

    async def revise_receipt_candidate(
        self, request: ReceiptCandidateRequest, expected_version: int
    ) -> ReceiptForReview:
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    row = await self._lock_receipt(con, request.receipt_id)
                    self._version(row, expected_version)
                    if row[6] not in {"NEEDS_REVIEW", "CONFIRMED"}:
                        raise MaterialReceiptError(Code.INVALID_RECEIPT_STATE)
                    existing = await (
                        await con.execute(
                            "SELECT receipt_item_id, status FROM material_receipt_items "
                            "WHERE receipt_id = %s FOR UPDATE",
                            (request.receipt_id,),
                        )
                    ).fetchall()
                    statuses = {item_id: status for item_id, status in existing}
                    requested_ids = {item.receipt_item_id for item in request.items}
                    active_ids = {
                        item_id for item_id, status in existing
                        if status not in {"CANCELLED", "REJECTED"}
                    }
                    if not active_ids.issubset(requested_ids):
                        raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR)
                    for item in request.items:
                        status = statuses.get(item.receipt_item_id)
                        if status in {"CANCELLED", "REJECTED", "POSTED"}:
                            raise MaterialReceiptError(Code.INVALID_ITEM_STATE)
                        if status is None:
                            await self._insert_item(con, request.receipt_id, item)
                        else:
                            await con.execute(
                                """
                                UPDATE material_receipt_items SET
                                    line_number = %s,
                                    candidate_material_description = %s,
                                    canonical_display_name = %s,
                                    size_description = %s, specification = %s,
                                    material_id = %s, full_colly_count = %s,
                                    qty_per_full_colly = %s, partial_qty = %s,
                                    total_qty = %s, unit = %s,
                                    status = 'NEEDS_REVIEW', updated_at = %s
                                WHERE receipt_item_id = %s AND receipt_id = %s
                                """,
                                _item_parameters(item)[1:]
                                + (datetime.now(timezone.utc), item.receipt_item_id, request.receipt_id),
                            )
                    await con.execute(
                        """
                        UPDATE material_receipts SET supplier_name = %s,
                            document_number = %s, document_date = %s, received_at = %s,
                            source_asset_reference = %s, status = 'NEEDS_REVIEW',
                            version = version + 1, confirmed_version = NULL,
                            confirmed_at = NULL, confirmation_actor_reference = NULL,
                            updated_at = %s
                        WHERE receipt_id = %s
                        """,
                        (
                            request.supplier_name, request.document_number,
                            request.document_date, request.received_at,
                            request.source_asset_reference, datetime.now(timezone.utc),
                            request.receipt_id,
                        ),
                    )
                    return await self._read(con, request.receipt_id)
        except MaterialReceiptError:
            raise
        except psycopg.OperationalError as exc:
            raise MaterialReceiptError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.Error as exc:
            raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR) from exc

    async def get_receipt_for_review(self, receipt_id: UUID) -> ReceiptForReview:
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    return await self._read(con, receipt_id)
        except MaterialReceiptError:
            raise
        except psycopg.OperationalError as exc:
            raise MaterialReceiptError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.Error as exc:
            raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR) from exc

    async def confirm_receipt(
        self, receipt_id: UUID, expected_version: int, actor_reference: str
    ) -> ReceiptForReview:
        _required_actor(actor_reference)
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    row = await self._lock_receipt(con, receipt_id)
                    self._version(row, expected_version)
                    if row[6] != "NEEDS_REVIEW":
                        raise MaterialReceiptError(Code.INVALID_RECEIPT_STATE)
                    items = await (
                        await con.execute(
                            "SELECT receipt_item_id, material_id, unit FROM "
                            "material_receipt_items WHERE receipt_id = %s AND "
                            "status NOT IN ('CANCELLED', 'REJECTED') ORDER BY line_number "
                            "FOR UPDATE",
                            (receipt_id,),
                        )
                    ).fetchall()
                    if not items:
                        raise MaterialReceiptError(Code.NO_POSTABLE_ITEMS)
                    for item_id, material_id, unit in items:
                        if material_id is None:
                            raise MaterialReceiptError(Code.MATERIAL_UNRESOLVED)
                        material = await (
                            await con.execute(
                                "SELECT unit, is_active FROM material_stock "
                                "WHERE material_id = %s",
                                (material_id,),
                            )
                        ).fetchone()
                        if material is None:
                            raise MaterialReceiptError(Code.MATERIAL_NOT_FOUND)
                        if not material[1]:
                            raise MaterialReceiptError(Code.MATERIAL_INACTIVE)
                        if unit != material[0]:
                            raise MaterialReceiptError(Code.UNIT_MISMATCH)
                    now = datetime.now(timezone.utc)
                    await con.execute(
                        "UPDATE material_receipt_items SET status = 'CONFIRMED', "
                        "updated_at = %s WHERE receipt_id = %s AND status NOT IN "
                        "('CANCELLED', 'REJECTED')",
                        (now, receipt_id),
                    )
                    await con.execute(
                        "UPDATE material_receipts SET status = 'CONFIRMED', "
                        "confirmed_version = version, confirmed_at = %s, "
                        "confirmation_actor_reference = %s, updated_at = %s "
                        "WHERE receipt_id = %s",
                        (now, actor_reference, now, receipt_id),
                    )
                    return await self._read(con, receipt_id)
        except MaterialReceiptError:
            raise
        except psycopg.OperationalError as exc:
            raise MaterialReceiptError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.Error as exc:
            raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR) from exc

    async def reject_receipt(
        self, receipt_id: UUID, expected_version: int, actor_reference: str
    ) -> ReceiptDecision:
        return await self._terminal(receipt_id, expected_version, actor_reference, "REJECTED")

    async def cancel_receipt(
        self, receipt_id: UUID, expected_version: int, actor_reference: str
    ) -> ReceiptDecision:
        return await self._terminal(receipt_id, expected_version, actor_reference, "CANCELLED")

    async def cancel_receipt_item(
        self, receipt_id: UUID, receipt_item_id: UUID, expected_version: int,
        actor_reference: str,
    ) -> ReceiptForReview:
        _required_actor(actor_reference)
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    row = await self._lock_receipt(con, receipt_id)
                    self._version(row, expected_version)
                    if row[6] not in {"NEEDS_REVIEW", "CONFIRMED"}:
                        raise MaterialReceiptError(Code.INVALID_RECEIPT_STATE)
                    item = await (
                        await con.execute(
                            "SELECT status FROM material_receipt_items WHERE "
                            "receipt_id = %s AND receipt_item_id = %s FOR UPDATE",
                            (receipt_id, receipt_item_id),
                        )
                    ).fetchone()
                    if item is None:
                        raise MaterialReceiptError(Code.RECEIPT_ITEM_NOT_FOUND)
                    if item[0] not in {"EXTRACTED", "NEEDS_REVIEW", "CONFIRMED"}:
                        raise MaterialReceiptError(Code.INVALID_ITEM_STATE)
                    now = datetime.now(timezone.utc)
                    await con.execute(
                        "UPDATE material_receipt_items SET status = 'CANCELLED', "
                        "updated_at = %s WHERE receipt_item_id = %s",
                        (now, receipt_item_id),
                    )
                    await con.execute(
                        "UPDATE material_receipts SET status = 'NEEDS_REVIEW', "
                        "version = version + 1, confirmed_version = NULL, "
                        "confirmed_at = NULL, confirmation_actor_reference = NULL, "
                        "updated_at = %s WHERE receipt_id = %s",
                        (now, receipt_id),
                    )
                    return await self._read(con, receipt_id)
        except MaterialReceiptError:
            raise
        except psycopg.OperationalError as exc:
            raise MaterialReceiptError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.Error as exc:
            raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR) from exc

    async def _terminal(self, receipt_id: UUID, expected_version: int,
                        actor_reference: str, status: str) -> ReceiptDecision:
        _required_actor(actor_reference)
        try:
            async with await psycopg.AsyncConnection.connect(self._database_url) as con:
                async with con.transaction():
                    row = await self._lock_receipt(con, receipt_id)
                    self._version(row, expected_version)
                    if row[6] not in {"EXTRACTED", "NEEDS_REVIEW", "CONFIRMED"}:
                        raise MaterialReceiptError(Code.INVALID_RECEIPT_STATE)
                    now = datetime.now(timezone.utc)
                    await con.execute(
                        "UPDATE material_receipt_items SET status = %s, updated_at = %s "
                        "WHERE receipt_id = %s AND status NOT IN ('CANCELLED','REJECTED')",
                        (status, now, receipt_id),
                    )
                    result = await (
                        await con.execute(
                            "UPDATE material_receipts SET status = %s, version = version + 1, "
                            "confirmed_version = NULL, confirmed_at = NULL, "
                            "confirmation_actor_reference = NULL, updated_at = %s "
                            "WHERE receipt_id = %s RETURNING version",
                            (status, now, receipt_id),
                        )
                    ).fetchone()
                    return ReceiptDecision(receipt_id, ReceiptStatus(status), result[0])
        except MaterialReceiptError:
            raise
        except psycopg.OperationalError as exc:
            raise MaterialReceiptError(Code.DATABASE_UNAVAILABLE) from exc
        except psycopg.Error as exc:
            raise MaterialReceiptError(Code.DATA_INTEGRITY_ERROR) from exc

    @staticmethod
    async def _insert_item(con: psycopg.AsyncConnection, receipt_id: UUID,
                           item: ReceiptItemCandidate) -> None:
        await con.execute(
            """
            INSERT INTO material_receipt_items (
                receipt_item_id, receipt_id, line_number,
                candidate_material_description, canonical_display_name,
                size_description, specification, material_id, full_colly_count,
                qty_per_full_colly, partial_qty, total_qty, unit
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (item.receipt_item_id, receipt_id) + _item_parameters(item)[1:],
        )

    @staticmethod
    async def _lock_receipt(con: psycopg.AsyncConnection, receipt_id: UUID):
        row = await (
            await con.execute(
                f"SELECT {_RECEIPT_COLUMNS} FROM material_receipts "
                "WHERE receipt_id = %s FOR UPDATE",
                (receipt_id,),
            )
        ).fetchone()
        if row is None:
            raise MaterialReceiptError(Code.RECEIPT_NOT_FOUND)
        return row

    @staticmethod
    def _version(row: tuple[object, ...], expected: int) -> None:
        if type(expected) is not int or expected <= 0 or row[7] != expected:
            raise MaterialReceiptError(Code.STALE_RECEIPT_VERSION)

    @staticmethod
    async def _read(con: psycopg.AsyncConnection, receipt_id: UUID) -> ReceiptForReview:
        row = await (
            await con.execute(
                f"SELECT {_RECEIPT_COLUMNS} FROM material_receipts WHERE receipt_id = %s",
                (receipt_id,),
            )
        ).fetchone()
        if row is None:
            raise MaterialReceiptError(Code.RECEIPT_NOT_FOUND)
        item_rows = await (
            await con.execute(
                f"SELECT {_ITEM_COLUMNS} FROM material_receipt_items "
                "WHERE receipt_id = %s ORDER BY line_number, receipt_item_id",
                (receipt_id,),
            )
        ).fetchall()
        return _map_receipt(row, tuple(_map_item(item) for item in item_rows))
