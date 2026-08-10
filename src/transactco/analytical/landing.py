"""The crossing: Postgres (operational) to DuckDB (analytical).

One direction only, and one file at the end of it. The whole warehouse is a
single embedded warehouse.duckdb -- no server, no container. Close the laptop
and the warehouse comes with you.

Landing does three things and refuses to do a fourth:

  1. copies public.* into raw.* exactly as found, including drift;
  2. records what it copied in raw._land_manifest;
  3. proves the answer key is unreachable from this connection.

The fourth thing is touching _control. This module connects as analytics_ro,
which has no grant on that schema at all, so the guarantee does not depend on
the code below being written correctly -- it depends on Postgres. verify_seal()
demonstrates that on every run by trying the read and showing you it failed.

raw.* is deliberately a faithful mirror. If schema_drift renamed a column, the
drifted name lands here, because a landing step that quietly repaired the source
would hide the exact failure the student is supposed to find.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import duckdb
import psycopg

from ..config import Settings
from ..operational.postgres import SOURCE_TABLES, readonly_connection

RAW_SCHEMA = "raw"
ANALYTICS_SCHEMA = "analytics"


@dataclass
class LandedTable:
    name: str
    row_count: int
    columns: list[str]


@dataclass
class LandResult:
    tables: list[LandedTable]
    seal_held: bool
    seal_message: str
    duckdb_path: str


def verify_seal(settings: Settings) -> tuple[bool, str]:
    """Try to read the answer key as analytics_ro. Success here is a failure.

    Returns (seal_held, message). seal_held is True when Postgres refused.
    """
    try:
        with readonly_connection(settings) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM _control.injected_incidents")
                count = cur.fetchone()[0]
        return False, (
            f"SEAL BROKEN: analytics_ro read {count} rows from _control.injected_incidents. "
            "Check infra/postgres/init/03_roles.sql."
        )
    except psycopg.errors.InsufficientPrivilege as exc:
        return True, f"sealed: {str(exc).strip().splitlines()[0]}"
    except psycopg.errors.UndefinedTable as exc:
        # The role cannot see the schema at all, so Postgres reports the table
        # as nonexistent rather than forbidden. Same guarantee.
        return True, f"sealed: {str(exc).strip().splitlines()[0]}"


def run_land(settings: Settings, progress=None) -> LandResult:
    def step(message: str) -> None:
        if progress is not None:
            progress(message)

    step("verifying the seal on _control")
    seal_held, seal_message = verify_seal(settings)
    if not seal_held:
        raise RuntimeError(seal_message)

    settings.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(settings.duckdb_path))
    landed: list[LandedTable] = []

    try:
        step("loading the duckdb postgres extension")
        con.execute("INSTALL postgres")
        con.execute("LOAD postgres")

        step("attaching postgres read-only")
        # ATTACH takes a literal, not a bound parameter, so the DSN is inlined
        # with its quotes escaped.
        dsn_literal = settings.readonly_dsn.replace("'", "''")
        con.execute(f"ATTACH '{dsn_literal}' AS pg (TYPE postgres, READ_ONLY)")
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

        for table in SOURCE_TABLES:
            step(f"landing raw.{table}")
            con.execute(
                f"CREATE OR REPLACE TABLE {RAW_SCHEMA}.{table} AS SELECT * FROM pg.public.{table}"
            )
            row_count = con.execute(f"SELECT count(*) FROM {RAW_SCHEMA}.{table}").fetchone()[0]
            columns = [
                row[0]
                for row in con.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = ? AND table_name = ? ORDER BY ordinal_position",
                    [RAW_SCHEMA, table],
                ).fetchall()
            ]
            landed.append(LandedTable(name=table, row_count=row_count, columns=columns))

        step("writing raw._land_manifest")
        con.execute(
            f"""
            CREATE OR REPLACE TABLE {RAW_SCHEMA}._land_manifest (
                table_name  VARCHAR,
                row_count   BIGINT,
                columns     VARCHAR,
                landed_at   TIMESTAMPTZ
            )
            """
        )
        landed_at = datetime.now(timezone.utc)
        con.executemany(
            f"INSERT INTO {RAW_SCHEMA}._land_manifest VALUES (?, ?, ?, ?)",
            [(t.name, t.row_count, ",".join(t.columns), landed_at) for t in landed],
        )

        # The contract the Incident Exercise detector writes into. Created empty and never
        # replaced, so re-landing does not wipe a student's detections.
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {ANALYTICS_SCHEMA}")
        con.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {ANALYTICS_SCHEMA}.detections (
                detection_id VARCHAR,
                defect_type  VARCHAR,
                target_table VARCHAR,
                row_key      VARCHAR,
                evidence     VARCHAR,
                detected_at  TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        con.execute("DETACH pg")

        step("asserting _control never crossed")
        leaked = con.execute(
            """
            SELECT table_schema || '.' || table_name
            FROM information_schema.tables
            WHERE lower(table_schema) LIKE '%control%' OR lower(table_name) LIKE '%injected%'
            """
        ).fetchall()
        if leaked:
            raise RuntimeError(f"answer key leaked into the warehouse: {[row[0] for row in leaked]}")

    finally:
        con.close()

    return LandResult(
        tables=landed,
        seal_held=seal_held,
        seal_message=seal_message,
        duckdb_path=str(settings.duckdb_path),
    )
