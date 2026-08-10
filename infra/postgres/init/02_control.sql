-- =============================================================================
-- TransactCo · _control (the sealed oracle)
--
-- This schema is the answer key. Every defect injected into public.* records
-- here exactly what was broken, when, and which rows were touched. On Day 4 the
-- student's detector is scored against this and nothing else.
--
-- It must never cross into DuckDB. That guarantee is enforced in 03_roles.sql
-- by permissions, not by the good behavior of the landing script -- an agent
-- pointed at this database on Day 4 has to be unable to read it, not merely
-- asked not to.
--
-- Two levels of truth, because the scoring question has two halves:
--   injected_incidents -> did the detector find the right defect?
--   incident_rows      -> did it find the right rows?
-- A detector that answers only the first half is the one that "sounds
-- plausible" without being correct.
-- =============================================================================

CREATE SCHEMA _control;

CREATE TABLE _control.injected_incidents (
    incident_id            TEXT PRIMARY KEY,
    run_id                 TEXT        NOT NULL,
    defect_type            TEXT        NOT NULL,
    severity               TEXT        NOT NULL,
    target_table           TEXT        NOT NULL,
    target_column          TEXT,
    affected_row_count     INTEGER     NOT NULL DEFAULT 0,
    business_window_start  TIMESTAMPTZ,
    business_window_end    TIMESTAMPTZ,

    -- False marks a decoy: a real event that looks like an incident and is not.
    -- Flagging it costs the detector precision. Without this column a detector
    -- that reports everything scores perfect recall.
    is_true_incident       BOOLEAN     NOT NULL DEFAULT TRUE,

    -- Set on the symptoms of multi_failure_cascade, pointing at the one deploy
    -- that caused them. Linking symptoms back to a single cause is the skill
    -- being tested.
    root_cause_incident_id TEXT        REFERENCES _control.injected_incidents (incident_id),

    detection_hint         TEXT        NOT NULL,
    notes                  TEXT,
    injected_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Row-level truth. target_table repeats here because a single incident can
-- corrupt more than one table -- a duplicated order also duplicates its payment.
CREATE TABLE _control.incident_rows (
    incident_id  TEXT NOT NULL REFERENCES _control.injected_incidents (incident_id) ON DELETE CASCADE,
    target_table TEXT NOT NULL,
    row_key      TEXT NOT NULL,
    PRIMARY KEY (incident_id, target_table, row_key)
);

CREATE INDEX idx_incident_rows_incident ON _control.incident_rows (incident_id);

-- Score history, so a student can see their second attempt beat their first.
CREATE TABLE _control.score_runs (
    score_run_id     TEXT PRIMARY KEY,
    scored_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    detections       INTEGER     NOT NULL,
    incidents_true   INTEGER     NOT NULL,
    incidents_caught INTEGER     NOT NULL,
    precision_score  NUMERIC(6, 4),
    recall_score     NUMERIC(6, 4),
    f1_score         NUMERIC(6, 4),
    detail           JSONB
);
