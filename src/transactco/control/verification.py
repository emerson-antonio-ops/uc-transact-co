"""Read-only readiness checks for the clean TransactCo teaching fixture."""

from __future__ import annotations

from dataclasses import dataclass

import duckdb

from ..analytical.landing import verify_seal
from ..config import Settings
from ..operational.postgres import SOURCE_TABLES, admin_connection, fetch_one
from ..operational.seed import assert_baseline_is_clean


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def run_verification(settings: Settings) -> list[Check]:
    """Verify the clean baseline, warehouse parity, and oracle isolation.

    This deliberately performs no reset, seed, injection, or write. Operators
    decide when those state-changing actions are appropriate, then run this as
    the evidence gate.
    """

    checks: list[Check] = []

    with admin_connection(settings) as conn:
        control_tables = {
            row[0]
            for row in conn.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = '_control'
                """
            ).fetchall()
        }
    required_control = {"injected_incidents", "incident_rows", "score_runs"}
    missing_control = sorted(required_control - control_tables)
    checks.append(
        Check(
            "oracle table inventory",
            not missing_control,
            "injected_incidents, incident_rows, score_runs present"
            if not missing_control
            else f"missing: {', '.join(missing_control)}",
        )
    )

    baseline_failures = assert_baseline_is_clean(settings)
    checks.append(
        Check(
            "clean Postgres baseline",
            not baseline_failures,
            "no unrecorded defects" if not baseline_failures else "; ".join(baseline_failures),
        )
    )

    seal_held, seal_message = verify_seal(settings)
    checks.append(Check("analytics oracle seal", seal_held, seal_message))

    if not settings.duckdb_path.exists():
        checks.append(
            Check(
                "DuckDB warehouse",
                False,
                f"{settings.duckdb_path.name} does not exist; run `make land`",
            )
        )
        return checks

    with admin_connection(settings) as conn:
        postgres_counts = {
            table: fetch_one(conn, f"SELECT count(*) FROM public.{table}")[0]
            for table in SOURCE_TABLES
        }

    warehouse = duckdb.connect(str(settings.duckdb_path), read_only=True)
    try:
        available = {
            row[0]
            for row in warehouse.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'raw'
                """
            ).fetchall()
        }
        missing = sorted(set(SOURCE_TABLES) - available)
        checks.append(
            Check(
                "raw table inventory",
                not missing,
                "customers, products, orders, payments present"
                if not missing
                else f"missing: {', '.join(missing)}",
            )
        )

        if not missing:
            duckdb_counts = {
                table: warehouse.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
                for table in SOURCE_TABLES
            }
            mismatches = {
                table: (postgres_counts[table], duckdb_counts[table])
                for table in SOURCE_TABLES
                if postgres_counts[table] != duckdb_counts[table]
            }
            detail = (
                ", ".join(f"{table}={count:,}" for table, count in postgres_counts.items())
                if not mismatches
                else "; ".join(
                    f"{table}: postgres={counts[0]:,}, duckdb={counts[1]:,}"
                    for table, counts in mismatches.items()
                )
            )
            checks.append(Check("Postgres/DuckDB row parity", not mismatches, detail))

        leaks = warehouse.execute(
            """
            SELECT table_schema || '.' || table_name
            FROM information_schema.tables
            WHERE lower(table_schema) LIKE '%control%'
               OR lower(table_name) LIKE '%injected%'
            ORDER BY 1
            """
        ).fetchall()
        checks.append(
            Check(
                "oracle absent from DuckDB",
                not leaks,
                "no control or injected-incident tables"
                if not leaks
                else ", ".join(row[0] for row in leaks),
            )
        )

        manifest_exists = warehouse.execute(
            """
            SELECT count(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw' AND table_name = '_land_manifest'
            """
        ).fetchone()[0]
        checks.append(
            Check(
                "landing manifest",
                bool(manifest_exists),
                "raw._land_manifest present"
                if manifest_exists
                else "raw._land_manifest missing",
            )
        )
    finally:
        warehouse.close()

    return checks
