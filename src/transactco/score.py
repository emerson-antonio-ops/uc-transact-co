"""Score the student's detector against the sealed oracle.

The question this answers is the one from Day 4: did it catch the right defect,
on the right rows -- or did it just sound plausible?

Those are scored separately and both are reported, because they fail
independently. A detector can name every incident correctly and be pointing at
the wrong rows, and a detector can find exactly the right rows for an incident
it has misnamed.

The detector writes into analytics.detections in warehouse.duckdb:

    detection_id  free-form id for your own grouping
    defect_type   one of the 14 names (see `transactco defects --list`)
    target_table  customers | products | orders | payments
    row_key       primary key of the offending row, as text; NULL when the
                  defect has no rows (schema_drift)
    evidence      free text, not scored, read out loud when reviewing
    detected_at   defaults to now()

One row per offending row. Reporting an incident with no rows still earns the
incident-level credit and scores 0 on rows.

Defect types are compared by family, so the slash-suffixed cascade symptoms
(multi_failure_cascade/null_customer and friends) are credited when the student
reports the root multi_failure_cascade -- and vice versa. Reporting one root
cause for one deploy is the correct answer, not three unrelated findings.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

import duckdb
from psycopg.types.json import Jsonb

from .config import Settings
from .db import admin_connection, execute, fetch_all


def _family(defect_type: str) -> str:
    """Cascade symptoms share the family of their root."""
    return defect_type.strip().lower().replace("-", "_").replace(" ", "_").split("/")[0]


@dataclass
class FamilyScore:
    family: str
    is_true_incident: bool
    severity: str
    detection_hint: str
    truth_rows: set[tuple[str, str]] = field(default_factory=set)
    detected_rows: set[tuple[str, str]] = field(default_factory=set)
    reported: bool = False

    @property
    def hits(self) -> set[tuple[str, str]]:
        return self.truth_rows & self.detected_rows

    @property
    def row_recall(self) -> float | None:
        if not self.truth_rows:
            return None
        return len(self.hits) / len(self.truth_rows)

    @property
    def row_precision(self) -> float | None:
        if not self.detected_rows:
            return None
        return len(self.hits) / len(self.detected_rows)


@dataclass
class ScoreResult:
    families: list[FamilyScore]
    false_positive_families: list[str]
    decoys_flagged: list[str]
    total_detections: int
    incidents_true: int
    incidents_caught: int
    precision: float
    recall: float
    f1: float
    score_run_id: str

    @property
    def true_families(self) -> list[FamilyScore]:
        return [f for f in self.families if f.is_true_incident]


class DetectionsMissing(RuntimeError):
    pass


def _load_detections(settings: Settings) -> list[tuple[str, str, str | None]]:
    if not settings.duckdb_path.exists():
        raise DetectionsMissing(
            f"{settings.duckdb_path} does not exist. Run `make land` first."
        )

    con = duckdb.connect(str(settings.duckdb_path), read_only=True)
    try:
        exists = con.execute(
            """
            SELECT count(*) FROM information_schema.tables
            WHERE table_schema = 'analytics' AND table_name = 'detections'
            """
        ).fetchone()[0]
        if not exists:
            raise DetectionsMissing(
                "analytics.detections is not in the warehouse. Run `make land` to create the "
                "contract table, then have the detector write into it."
            )
        return con.execute(
            "SELECT defect_type, target_table, row_key FROM analytics.detections"
        ).fetchall()
    finally:
        con.close()


def run_score(settings: Settings, persist: bool = True) -> ScoreResult:
    detections = _load_detections(settings)

    with admin_connection(settings) as conn:
        incidents = fetch_all(
            conn,
            """
            SELECT defect_type, severity, is_true_incident, detection_hint
            FROM _control.injected_incidents
            ORDER BY defect_type
            """,
        )
        truth_rows = fetch_all(
            conn,
            """
            SELECT i.defect_type, r.target_table, r.row_key
            FROM _control.incident_rows r
            JOIN _control.injected_incidents i ON i.incident_id = r.incident_id
            """,
        )

        if not incidents:
            raise RuntimeError(
                "The answer key is empty -- nothing has been injected yet. Run `make inject`."
            )

        families: dict[str, FamilyScore] = {}
        for defect_type, severity, is_true, hint in incidents:
            key = _family(defect_type)
            existing = families.get(key)
            if existing is None:
                families[key] = FamilyScore(
                    family=key,
                    is_true_incident=is_true,
                    severity=severity,
                    detection_hint=hint,
                )
            else:
                # The cascade root carries the hint worth reading; symptoms
                # inherit truth-ness from any true member of the family.
                existing.is_true_incident = existing.is_true_incident or is_true

        for defect_type, table, row_key in truth_rows:
            families[_family(defect_type)].truth_rows.add((table, row_key))

        reported_families: set[str] = set()
        for defect_type, table, row_key in detections:
            if defect_type is None:
                continue
            key = _family(defect_type)
            reported_families.add(key)
            if key in families:
                families[key].reported = True
                if row_key is not None and table is not None:
                    families[key].detected_rows.add((table, str(row_key)))

        known = set(families)
        false_positive_families = sorted(reported_families - known)
        decoys_flagged = sorted(
            key for key in reported_families
            if key in families and not families[key].is_true_incident
        )

        true_families = [f for f in families.values() if f.is_true_incident]
        incidents_true = len(true_families)
        incidents_caught = sum(1 for f in true_families if f.reported)

        # Everything reported that was not a real incident counts against
        # precision: unknown names, and the decoy.
        wrong_reports = len(false_positive_families) + len(decoys_flagged)
        total_reported = incidents_caught + wrong_reports

        recall = incidents_caught / incidents_true if incidents_true else 0.0
        precision = incidents_caught / total_reported if total_reported else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

        score_run_id = f"score-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        result = ScoreResult(
            families=sorted(families.values(), key=lambda f: (not f.is_true_incident, f.family)),
            false_positive_families=false_positive_families,
            decoys_flagged=decoys_flagged,
            total_detections=len(detections),
            incidents_true=incidents_true,
            incidents_caught=incidents_caught,
            precision=precision,
            recall=recall,
            f1=f1,
            score_run_id=score_run_id,
        )

        if persist:
            detail = {
                "families": [
                    {
                        "family": f.family,
                        "is_true_incident": f.is_true_incident,
                        "reported": f.reported,
                        "truth_rows": len(f.truth_rows),
                        "detected_rows": len(f.detected_rows),
                        "hits": len(f.hits),
                        "row_recall": f.row_recall,
                        "row_precision": f.row_precision,
                    }
                    for f in result.families
                ],
                "false_positive_families": false_positive_families,
                "decoys_flagged": decoys_flagged,
            }
            execute(
                conn,
                """
                INSERT INTO _control.score_runs
                    (score_run_id, detections, incidents_true, incidents_caught,
                     precision_score, recall_score, f1_score, detail)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    score_run_id,
                    len(detections),
                    incidents_true,
                    incidents_caught,
                    round(precision, 4),
                    round(recall, 4),
                    round(f1, 4),
                    Jsonb(detail),
                ),
            )
            conn.commit()

    return result
