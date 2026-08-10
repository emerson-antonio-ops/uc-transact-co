"""Command line entry point. Everything here is reachable through the Makefile.

`status` deliberately does not report whether anything has been injected. On
Incident Exercise the injection is silent -- the student is supposed to notice that the
numbers in the mart are wrong, not read it off a status line. Only `reveal`
opens the oracle.
"""

from __future__ import annotations

import argparse
import sys
from datetime import timezone

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from .config import load_settings
from .db import SOURCE_TABLES, admin_connection, column_exists, fetch_all, fetch_one, wait_for_postgres
from .defects import ALL_DEFECTS, DEFECT_REGISTRY, SCENARIOS, clear_answer_key, load_answer_key, run_injection
from .land import run_land, verify_seal
from .score import DetectionsMissing, run_score
from .seed import assert_baseline_is_clean, run_seed
from .verify import run_verification

console = Console()


def _progress(message: str) -> None:
    console.print(f"  [dim]{message}[/dim]")


def _format_utc(value) -> str:
    """Render source and warehouse timestamps on one explicit clock."""
    if value is None:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def cmd_doctor(args) -> int:
    settings = load_settings()
    console.print(Panel.fit("TransactCo · doctor", style="bold cyan"))

    console.print(f"  postgres  [dim]{settings.pg_host}:{settings.pg_port}/{settings.pg_db}[/dim]")
    try:
        wait_for_postgres(settings, attempts=args.attempts, delay=1.0)
    except RuntimeError as exc:
        console.print(f"  [red]unreachable[/red] — {exc}")
        console.print("  [yellow]run `make up` first[/yellow]")
        return 1
    console.print("  [green]reachable[/green]")

    with admin_connection(settings) as conn:
        missing = [t for t in SOURCE_TABLES if not column_exists(conn, t, "ingested_at")]
        if missing:
            console.print(f"  [red]schema incomplete[/red] — missing tables: {', '.join(missing)}")
            return 1
        console.print("  [green]schema applied[/green]")

        drifted = column_exists(conn, "payments", "amount_paid")
        if drifted:
            console.print("  [yellow]payments.amount is currently drifted to amount_paid[/yellow]")

    seal_held, seal_message = verify_seal(settings)
    if seal_held:
        console.print("  [green]oracle sealed[/green] — analytics_ro cannot read _control")
    else:
        console.print(f"  [red]{seal_message}[/red]")
        return 1

    try:
        import duckdb

        con = duckdb.connect()
        con.execute("INSTALL postgres")
        con.execute("LOAD postgres")
        con.close()
        console.print("  [green]duckdb postgres extension ready[/green]")
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the operator
        console.print(f"  [red]duckdb extension unavailable[/red] — {exc}")
        console.print("  [yellow]this needs network on first run; do it before class[/yellow]")
        return 1

    console.print("\n[bold green]ready[/bold green]")
    return 0


def cmd_seed(args) -> int:
    settings = load_settings()
    console.print(Panel.fit("TransactCo · seed", style="bold cyan"))
    wait_for_postgres(settings)

    result = run_seed(settings, progress=_progress)

    table = Table(show_header=True, header_style="bold")
    table.add_column("table")
    table.add_column("rows", justify="right")
    table.add_row("customers", f"{result.customers:,}")
    table.add_row("products", f"{result.products:,}")
    table.add_row("orders", f"{result.orders:,}")
    table.add_row("payments", f"{result.payments:,}")
    console.print(table)
    console.print(
        f"  [dim]window {result.window_start:%Y-%m-%d} to {result.window_end:%Y-%m-%d} "
        f"· seed {settings.seed}[/dim]"
    )

    console.print("\n  verifying the baseline is clean")
    failures = assert_baseline_is_clean(settings)
    if failures:
        console.print("  [red]baseline is NOT clean:[/red]")
        for failure in failures:
            console.print(f"    [red]· {failure}[/red]")
        console.print("  [yellow]a detector would find defects the answer key never recorded[/yellow]")
        return 1

    console.print("  [green]clean[/green] — no incident exists until you inject one")
    return 0


def cmd_land(args) -> int:
    settings = load_settings()
    console.print(Panel.fit("TransactCo · land", style="bold cyan"))
    wait_for_postgres(settings)

    result = run_land(settings, progress=_progress)

    table = Table(show_header=True, header_style="bold")
    table.add_column("raw table")
    table.add_column("rows", justify="right")
    table.add_column("columns", justify="right")
    for landed in result.tables:
        table.add_row(f"raw.{landed.name}", f"{landed.row_count:,}", str(len(landed.columns)))
    console.print(table)
    console.print(f"  [green]{result.seal_message}[/green]")
    console.print(f"  [dim]warehouse: {result.duckdb_path}[/dim]")
    return 0


def cmd_inject(args) -> int:
    settings = load_settings()

    if args.list:
        table = Table(show_header=True, header_style="bold")
        table.add_column("defect")
        table.add_column("in scenarios")
        for name in ALL_DEFECTS:
            scenarios = [s for s, members in SCENARIOS.items() if name in members]
            table.add_row(name, ", ".join(scenarios) or "[dim]—[/dim]")
        console.print(table)
        console.print(f"  [dim]scenarios: {', '.join(SCENARIOS)}[/dim]")
        return 0

    if args.defect:
        unknown = [d for d in args.defect if d not in DEFECT_REGISTRY]
        if unknown:
            console.print(f"[red]unknown defect(s): {', '.join(unknown)}[/red]")
            return 1
        # Preserve the canonical order even when named individually, because
        # schema_drift has to be last and slow_source has to follow anything
        # that needs a payment row to exist.
        selected = [d for d in ALL_DEFECTS if d in set(args.defect)]
    else:
        if args.scenario not in SCENARIOS:
            console.print(f"[red]unknown scenario: {args.scenario}[/red]")
            return 1
        selected = SCENARIOS[args.scenario]

    wait_for_postgres(settings)

    if args.quiet:
        # The Incident Exercise default: nothing on screen that tells the room what landed.
        result = run_injection(settings, selected, force=args.force)
        console.print("[dim]done.[/dim]")
        return 0

    console.print(Panel.fit("TransactCo · inject", style="bold red"))
    result = run_injection(settings, selected, force=args.force, progress=_progress)

    if result.incidents:
        console.print(
            f"  [red]{len(result.incidents)} incident(s) injected[/red] "
            f"· {result.total_rows:,} rows sealed in the answer key"
        )
    if result.skipped:
        console.print(f"  [yellow]skipped (already injected): {', '.join(result.skipped)}[/yellow]")
        console.print("  [dim]use --force to inject again, or `make reset` for a clean database[/dim]")
    if not result.incidents and not result.skipped:
        console.print("  [yellow]nothing injected[/yellow]")

    console.print("  [dim]run `make land` to carry it into the warehouse[/dim]")
    return 0


def cmd_reveal(args) -> int:
    settings = load_settings()
    incidents = load_answer_key(settings)
    if not incidents:
        console.print("[yellow]the answer key is empty — nothing has been injected[/yellow]")
        return 0

    console.print(Panel.fit("TransactCo · the sealed oracle", style="bold magenta"))

    # One block per incident rather than a wide table: the detection hints are
    # full sentences and a column layout shreds them on a projector.
    for incident in incidents:
        is_true = incident["is_true_incident"]
        name = incident["defect_type"]
        target = incident["target_table"]
        if incident["target_column"]:
            target = f"{target}.{incident['target_column']}"

        label = f"[red]{name}[/red]" if is_true else f"[green]{name}[/green]"
        tag = "" if is_true else " [green](decoy — not an incident)[/green]"
        console.print(
            f"\n  {label}{tag}\n"
            f"  [dim]{incident['severity']} · {target} · "
            f"{incident['affected_row_count']:,} rows[/dim]"
        )
        console.print(Padding(incident["detection_hint"], (0, 0, 0, 4)), highlight=False)
        if incident["notes"]:
            console.print(
                Padding(f"[dim]{incident['notes']}[/dim]", (0, 0, 0, 4)), highlight=False
            )

    console.print(
        "\n  [dim]green is a decoy: a real event that is not an incident. "
        "Flagging it costs precision.[/dim]"
    )
    return 0


def cmd_score(args) -> int:
    settings = load_settings()
    try:
        result = run_score(settings)
    except DetectionsMissing as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        return 1
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1

    console.print(Panel.fit("TransactCo · detector vs oracle", style="bold magenta"))

    table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    table.add_column("incident", no_wrap=True)
    table.add_column("verdict", no_wrap=True)
    table.add_column("rows", justify="right", no_wrap=True)
    table.add_column("recall", justify="right", no_wrap=True)
    table.add_column("prec", justify="right", no_wrap=True)

    for family in result.families:
        if not family.is_true_incident:
            verdict = "[red]FLAGGED A DECOY[/red]" if family.reported else "[green]correctly ignored[/green]"
        else:
            verdict = "[green]CAUGHT[/green]" if family.reported else "[red]MISSED[/red]"

        def pct(value):
            return "—" if value is None else f"{value:.0%}"

        table.add_row(
            family.family,
            verdict,
            f"{len(family.hits):,} / {len(family.truth_rows):,}" if family.truth_rows else "—",
            pct(family.row_recall),
            pct(family.row_precision),
        )

    console.print(table)

    if result.false_positive_families:
        console.print(
            f"  [red]reported but never injected: {', '.join(result.false_positive_families)}[/red]"
        )

    console.print()
    console.print(
        f"  incidents caught  [bold]{result.incidents_caught}/{result.incidents_true}[/bold]\n"
        f"  precision         [bold]{result.precision:.0%}[/bold]\n"
        f"  recall            [bold]{result.recall:.0%}[/bold]\n"
        f"  f1                [bold]{result.f1:.0%}[/bold]\n"
        f"  [dim]{result.total_detections:,} detections read · saved as {result.score_run_id}[/dim]"
    )
    return 0


def cmd_status(args) -> int:
    settings = load_settings()
    wait_for_postgres(settings)
    console.print(Panel.fit("TransactCo · status", style="bold cyan"))

    with admin_connection(settings) as conn:
        table = Table(show_header=True, header_style="bold")
        table.add_column("table")
        table.add_column("rows", justify="right")
        table.add_column("latest business time")
        table.add_column("latest ingest")

        time_columns = {
            "customers": "created_at",
            "products": "created_at",
            "orders": "ordered_at",
            "payments": "paid_at",
        }
        for name in SOURCE_TABLES:
            row = fetch_one(
                conn,
                f"SELECT count(*), max({time_columns[name]}), max(ingested_at) FROM public.{name}",
            )
            count, business_max, ingest_max = row
            table.add_row(
                f"public.{name}",
                f"{count:,}",
                _format_utc(business_max),
                _format_utc(ingest_max),
            )
        console.print(table)

        if column_exists(conn, "payments", "amount_paid"):
            console.print("  [yellow]payments.amount is not present under that name right now[/yellow]")

    if settings.duckdb_path.exists():
        import duckdb

        con = duckdb.connect(str(settings.duckdb_path), read_only=True)
        try:
            manifest = con.execute(
                "SELECT table_name, row_count, landed_at FROM raw._land_manifest ORDER BY table_name"
            ).fetchall()
            detections = con.execute(
                """
                SELECT count(*) FROM information_schema.tables
                WHERE table_schema = 'analytics' AND table_name = 'detections'
                """
            ).fetchone()[0]
            detection_count = (
                con.execute("SELECT count(*) FROM analytics.detections").fetchone()[0]
                if detections
                else 0
            )
        except duckdb.Error:
            manifest, detection_count = [], 0
        finally:
            con.close()

        if manifest:
            console.print(
                f"  warehouse [dim]{settings.duckdb_path.name}[/dim] · "
                f"landed {_format_utc(manifest[0][2])}"
            )
            console.print(f"  [dim]{', '.join(f'raw.{m[0]} {m[1]:,}' for m in manifest)}[/dim]")
        console.print(f"  detections written by the detector: [bold]{detection_count:,}[/bold]")
    else:
        console.print(f"  [yellow]no warehouse yet[/yellow] — run `make land`")

    return 0


def cmd_verify(args) -> int:
    settings = load_settings()
    wait_for_postgres(settings)
    console.print(Panel.fit("TransactCo · verify", style="bold cyan"))

    checks = run_verification(settings)
    failed = False
    for check in checks:
        if check.passed:
            console.print(f"  [green]PASS[/green]  {check.name} — [dim]{check.detail}[/dim]")
        else:
            failed = True
            console.print(f"  [red]FAIL[/red]  {check.name} — {check.detail}")

    if failed:
        console.print("\n[bold red]not ready[/bold red]")
        return 1

    console.print("\n[bold green]verified[/bold green]")
    return 0


def cmd_defects(args) -> int:
    table = Table(show_header=True, header_style="bold")
    table.add_column("defect")
    table.add_column("in scenarios")
    for name in ALL_DEFECTS:
        scenarios = [s for s, members in SCENARIOS.items() if name in members]
        table.add_row(name, ", ".join(scenarios) or "[dim]—[/dim]")
    console.print(table)
    return 0


def cmd_clear(args) -> int:
    settings = load_settings()
    removed = clear_answer_key(settings)
    console.print(f"[yellow]cleared {removed} incident(s) from the answer key[/yellow]")
    console.print("[dim]the corrupted rows are still in public.* — run `make reset` for a clean database[/dim]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="transactco", description="TransactCo brownfield base")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="check the environment before class")
    doctor.add_argument("--attempts", type=int, default=30)
    doctor.set_defaults(func=cmd_doctor)

    seed = sub.add_parser("seed", help="load correlated data and verify the baseline is clean")
    seed.set_defaults(func=cmd_seed)

    land = sub.add_parser("land", help="carry public.* into raw.* in the DuckDB warehouse")
    land.set_defaults(func=cmd_land)

    inject = sub.add_parser("inject", help="inject defects and seal the answer key")
    inject.add_argument("--scenario", default="live", help=f"one of: {', '.join(SCENARIOS)}")
    inject.add_argument("--defect", action="append", help="inject specific defects by name (repeatable)")
    inject.add_argument("--force", action="store_true", help="inject again even if already present")
    inject.add_argument("--quiet", action="store_true", help="say nothing about what landed")
    inject.add_argument("--list", action="store_true", help="list defects and exit")
    inject.set_defaults(func=cmd_inject)

    reveal = sub.add_parser("reveal", help="open the sealed oracle")
    reveal.set_defaults(func=cmd_reveal)

    score = sub.add_parser("score", help="score analytics.detections against the oracle")
    score.set_defaults(func=cmd_score)

    status = sub.add_parser("status", help="row counts and freshness, no spoilers")
    status.set_defaults(func=cmd_status)

    verify = sub.add_parser("verify", help="verify the clean baseline, landing parity and seal")
    verify.set_defaults(func=cmd_verify)

    defects = sub.add_parser("defects", help="list the 14 defects")
    defects.set_defaults(func=cmd_defects)

    clear = sub.add_parser("clear-key", help="empty the answer key without touching public.*")
    clear.set_defaults(func=cmd_clear)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]interrupted[/yellow]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
