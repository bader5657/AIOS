"""Positive admission gate for material-boundary PostgreSQL tests."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import psycopg
from psycopg import conninfo


OPT_IN = "AIOS_MATERIAL_DISPOSABLE_TESTS"
TEST_URL = "AIOS_MATERIAL_TEST_DATABASE_URL"
_TEST_DATABASE = re.compile(r"^aios_material_disposable_[a-z0-9_]+$")
_GOVERNED_USERS = {
    "aios",
    "aios_material_receipt_candidate_runtime",
    "aios_material_inventory_posting_runtime",
    "aios_material_stock_reader",
}
_GOVERNED_PASSWORD_KEYS = {
    "AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD",
    "AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD",
    "AIOS_MATERIAL_STOCK_DB_PASSWORD",
    "AIOS_MATERIAL_STOCK_READER_DB_PASSWORD",
}
_ALLOWED_CONNINFO_KEYS = {"host", "port", "dbname", "user", "password", "sslmode"}


@dataclass(frozen=True, slots=True)
class DisposablePostgresTarget:
    url: str = field(repr=False)
    host: str
    port: int
    dbname: str
    admin_user: str
    password: str = field(repr=False)


def admit_disposable_postgres(
    database_url: str | None,
    *,
    environment: dict[str, str] | None = None,
) -> DisposablePostgresTarget:
    """Return a target only after every positive disposable invariant passes."""

    env = os.environ if environment is None else environment
    if env.get(OPT_IN) != "1":
        raise RuntimeError("explicit disposable PostgreSQL opt-in is required")
    if not isinstance(database_url, str) or not database_url.strip():
        raise RuntimeError("disposable PostgreSQL URL is required")
    try:
        parsed = conninfo.conninfo_to_dict(database_url)
        host = parsed.get("host")
        port_text = parsed.get("port")
        dbname = parsed.get("dbname")
        user = parsed.get("user")
        password = parsed.get("password")
        port = int(port_text) if port_text is not None else 5432
    except (psycopg.Error, TypeError, ValueError) as exc:
        raise RuntimeError("disposable PostgreSQL target is malformed") from exc
    if set(parsed) - _ALLOWED_CONNINFO_KEYS:
        raise RuntimeError("disposable PostgreSQL target is ambiguous")
    if parsed.get("sslmode") not in {None, "disable"}:
        raise RuntimeError("disposable PostgreSQL transport is not admitted")
    if host != "127.0.0.1" or port == 5432 or not 1024 <= port <= 65535:
        raise RuntimeError("disposable PostgreSQL endpoint is not admitted")
    if not isinstance(dbname, str) or not _TEST_DATABASE.fullmatch(dbname):
        raise RuntimeError("disposable PostgreSQL database name is not admitted")
    if user != "postgres" or user in _GOVERNED_USERS:
        raise RuntimeError("disposable PostgreSQL setup identity is not admitted")
    if not isinstance(password, str) or not password:
        raise RuntimeError("disposable PostgreSQL password is required")
    governed_passwords = {
        env[key] for key in _GOVERNED_PASSWORD_KEYS if env.get(key)
    }
    if password in governed_passwords:
        raise RuntimeError("governed runtime credentials are prohibited in tests")
    return DisposablePostgresTarget(
        database_url, host, port, dbname, user, password
    )
