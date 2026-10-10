"""Minimum private-chat customer workflow; transaction boundary is injected.

Only the Telegram adapter supplies Actor from a received Telegram update.
This object is transport evidence, never enrollment or an approval receipt.
"""
from dataclasses import dataclass
from datetime import timedelta
import json
import re
import secrets
from uuid import uuid4

from core.app.customer_application import CustomerApplication
from core.app.customer_draft import CustomerDraft
from core.domain.customer import CustomerId
from core.domain.exceptions import DomainValidationError

@dataclass(frozen=True)
class Actor:
    user_id: int
    chat_id: int
    chat_type: str
    is_bot: bool

def _positive_id(value):
    return type(value) is int and 0 < value < 2**63

def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result

def _snapshot(payload):
    data = json.loads(payload, object_pairs_hook=_object)
    if type(data) is not dict or set(data) - {"name", "address", "city", "notes"}:
        raise ValueError("unexpected fields")
    return CustomerDraft(**data).snapshot()

class CustomerRegistration:
    """One transaction per message; reply only after the context commits."""

    def __init__(self, transactions):
        self._transactions = transactions

    def handle(self, actor, message_id, text):
        if type(text) is not str:
            return None
        command, _, payload = text.partition(" ")
        if command not in ("catat_pelanggan", "konfirmasi_pelanggan"):
            return None
        if (
            not isinstance(actor, Actor)
            or not _positive_id(actor.user_id)
            or not _positive_id(actor.chat_id)
            or not _positive_id(message_id)
            or actor.chat_type != "private"
            or actor.chat_id != actor.user_id
            or actor.is_bot is not False
        ):
            return "Akses ditolak."
        with self._transactions() as tx:
            owner = tx.lock_owner()
            if owner is None or owner[0] != actor.user_id or owner[1] is not True:
                return "Akses ditolak."
            if command == "catat_pelanggan":
                reply = self._prepare(tx, actor, message_id, payload, owner[2])
            else:
                reply = self._confirm(tx, actor, message_id, payload)
        return reply

    def invalidate_edit(self, actor, message_id):
        if (not isinstance(actor, Actor) or not _positive_id(actor.user_id)
                or not _positive_id(actor.chat_id) or not _positive_id(message_id)
                or actor.chat_type != "private" or actor.chat_id != actor.user_id
                or actor.is_bot is not False):
            return "Akses ditolak."
        with self._transactions() as tx:
            owner = tx.lock_owner()
            if owner is None or owner[0] != actor.user_id or owner[1] is not True:
                return "Akses ditolak."
            if message_id == owner[2]:
                tx.advance_draft(message_id)
        return "Edit tidak disimpan. Konfirmasi draft terkait dibatalkan; kirim draft baru."

    def _prepare(self, tx, actor, message_id, payload, last_message_id):
        # Telegram message IDs are monotonic within this private chat.
        # Stale deliveries must never invalidate a newer draft.
        previous = tx.by_request(message_id)
        if message_id <= last_message_id:
            if previous and message_id == last_message_id:
                try:
                    same_snapshot = previous["snapshot"] == _snapshot(payload)
                except (ValueError, TypeError, DomainValidationError):
                    same_snapshot = False
                if same_snapshot and previous["state"] == "consumed":
                    return self._receipt(previous["customer_id"])
                if same_snapshot and previous["state"] == "pending" and tx.clock() < previous["expires_at"]:
                    return self._preview(previous)
            return "Draft lama tidak berlaku; kirim pesan catat_pelanggan baru."
        # A malformed replacement is still an edit and cancels the old prompt.
        tx.advance_draft(message_id)
        try:
            if len(payload) > 3500:
                raise ValueError("payload too large")
            snapshot = _snapshot(payload)
            if len(json.dumps(snapshot, ensure_ascii=False)) > 3000:
                raise ValueError("preview too large")
        except (ValueError, TypeError, DomainValidationError):
            return ('Data tidak valid. Gunakan catat_pelanggan '
                    '{"name":"Ani","address":"Jalan 1","city":"Solo","notes":null}')
        now = tx.clock()
        row = dict(
            token=secrets.token_hex(32), owner_id=actor.user_id,
            chat_id=actor.chat_id, message_id=message_id, snapshot=snapshot,
            created_at=now, expires_at=now + timedelta(minutes=10),
            state="pending", customer_id=None,
        )
        tx.add_confirmation(row)
        return self._preview(row)

    def _confirm(self, tx, actor, message_id, token):
        if not re.fullmatch(r"[0-9a-f]{64}", token):
            return "Konfirmasi tidak valid."
        row = tx.by_token(token)
        if row is None:
            return "Konfirmasi tidak valid."
        if (row["owner_id"], row["chat_id"]) != (actor.user_id, actor.chat_id) or message_id <= row["message_id"]:
            return "Akses ditolak."
        if row["state"] == "consumed":
            return self._receipt(row["customer_id"])
        if row["state"] != "pending":
            return "Konfirmasi tidak berlaku; kirim draft baru."
        if tx.clock() >= row["expires_at"]:
            return "Konfirmasi kedaluwarsa; kirim draft baru."
        customer_id = "tg-customer-" + token
        customer = CustomerApplication().create_customer_from_draft(
            CustomerDraft(**row["snapshot"]), CustomerId(customer_id),
            event_id_source=lambda: str(uuid4()), occurred_at_source=tx.clock,
        )
        tx.save_customer(customer)
        tx.audit(row, customer_id)
        tx.consume(token, customer_id)
        return self._receipt(customer_id)

    @staticmethod
    def _preview(row):
        # Plain text; JSON escapes prevent notes from impersonating instructions.
        snapshot = json.dumps(row["snapshot"], ensure_ascii=False, sort_keys=True)
        return ("Periksa data pelanggan:\n" + snapshot +
                "\nBerlaku paling lama 600 detik sejak dibuat (retry tidak memperpanjang)." +
                "\nKirim: konfirmasi_pelanggan " + row["token"])

    @staticmethod
    def _receipt(customer_id):
        return "Pelanggan tersimpan. ID: " + customer_id
