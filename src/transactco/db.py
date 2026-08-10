"""Postgres helpers shared by the seeder, the injector and the scorer."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import psycopg

from .config import Settings

SOURCE_TABLES = ("customers", "products", "orders", "payments")


@contextmanager
def admin_connection(settings: Settings) -> Iterator[psycopg.Connection]:
    with psycopg.connect(settings.admin_dsn, autocommit=False) as conn:
        yield conn


@contextmanager
def readonly_connection(settings: Settings) -> Iterator[psycopg.Connection]:
    with psycopg.connect(settings.readonly_dsn, autocommit=True) as conn:
        yield conn


def fetch_all(conn: psycopg.Connection, sql: str, params: Any = None) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_one(conn: psycopg.Connection, sql: str, params: Any = None) -> tuple | None:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_column(conn: psycopg.Connection, sql: str, params: Any = None) -> list:
    return [row[0] for row in fetch_all(conn, sql, params)]


def execute(conn: psycopg.Connection, sql: str, params: Any = None) -> int:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


def column_exists(conn: psycopg.Connection, table: str, column: str) -> bool:
    row = fetch_one(
        conn,
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    return row is not None


def wait_for_postgres(settings: Settings, attempts: int = 30, delay: float = 1.0) -> None:
    """Block until Postgres accepts a connection, or raise the last error."""
    import time

    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            with psycopg.connect(settings.admin_dsn, connect_timeout=3):
                return
        except psycopg.OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Postgres never became reachable at {settings.pg_host}:{settings.pg_port}") from last_error
