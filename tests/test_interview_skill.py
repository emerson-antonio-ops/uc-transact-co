"""Executable contract tests for the interview-the-system giveaway skill."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / "skills/interview-the-system"
VALIDATOR = PROJECT_ROOT / "skills/interview-the-system/scripts/validate_investigation.py"


def valid_package() -> dict:
    return {
        "schema_version": "1.0",
        "status": "pending human review",
        "question": "Which physical records could support a revenue definition?",
        "outcome": "Separate available evidence from required business decisions.",
        "scope": {"in": ["local Postgres"], "out": ["production"]},
        "authority": {
            "read_only": True,
            "allowed_tools": ["read-only SQL"],
            "prohibited_actions": ["writes", "schema changes"],
            "stop_conditions": ["sensitive data", "business authority required"],
        },
        "context_sources": [
            {
                "id": "schema",
                "kind": "current",
                "location": "infra/postgres/init/01_schema.sql",
                "purpose": "Identify physical tables and columns.",
                "freshness": "current commit",
                "authority": "Physical schema only.",
            }
        ],
        "claims": [
            {
                "id": "claim-payment-table",
                "statement": "The operational model contains payment records.",
                "classification": "fact",
                "evidence_references": ["schema"],
            },
            {
                "id": "claim-revenue-candidate",
                "statement": "Payment amount is a candidate revenue input.",
                "classification": "inference",
                "reasoning": "The table records payment attempts and captures, but no revenue contract.",
                "evidence_references": ["schema"],
            },
            {
                "id": "claim-owner",
                "statement": "Finance will own the revenue definition.",
                "classification": "decision",
                "owner": "Finance owner",
                "evidence_references": [],
            },
            {
                "id": "claim-statuses",
                "statement": "Which payment statuses count?",
                "classification": "question",
                "owner": "Finance owner",
                "next_action": "Confirm the recognized statuses.",
                "evidence_references": [],
            },
        ],
        "ontology": {
            "entities": [{"name": "Payment", "status": "evidenced"}],
            "concepts": [
                {
                    "name": "Revenue",
                    "status": "unresolved",
                    "owner": "Finance owner",
                    "questions": ["Which statuses count?"],
                }
            ],
            "events": [],
            "relationships": [
                {
                    "subject": "Payment",
                    "predicate": "may_contribute_to",
                    "object": "Revenue",
                    "status": "unresolved",
                    "owner": "Finance owner",
                    "questions": ["Which statuses count?"],
                    "evidence_references": ["claim-revenue-candidate"],
                }
            ],
            "rules": [],
        },
        "open_questions": [
            {
                "question": "Which payment statuses count?",
                "owner": "Finance owner",
                "next_action": "Confirm the revenue contract.",
            }
        ],
    }


VALID_BRIEF = """# Technical Brief

## Status
pending human review

## Question and Outcome
Question and outcome.

## Scope and Authority
Read-only local system.

## Evidence Consulted
Current schema.

## Findings
Physical records exist; meaning is unresolved.

## Ontology
Payment may contribute to Revenue.

## Decisions and Open Questions
Finance must define recognized statuses.

## Risks and Stop Conditions
Stop before inventing business meaning.

## Human Review
Pending Finance review.
"""


class InterviewSkillTests(unittest.TestCase):
    def test_skill_metadata_is_discoverable(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        frontmatter = content.split("---", 2)[1]
        fields = {
            line.split(":", 1)[0].strip()
            for line in frontmatter.splitlines()
            if ":" in line
        }
        self.assertEqual({"name", "description"}, fields)
        self.assertIn("name: interview-the-system", frontmatter)
        self.assertIn("Use when", frontmatter)

        agent_metadata = (SKILL_ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Interview the System"', agent_metadata)
        self.assertIn("short_description:", agent_metadata)
        self.assertIn("$interview-the-system", agent_metadata)

    def run_validator(self, package: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            investigation = root / "investigation.json"
            brief = root / "technical-brief.md"
            trace = root / "trace.jsonl"
            investigation.write_text(json.dumps(package), encoding="utf-8")
            brief.write_text(VALID_BRIEF, encoding="utf-8")
            trace.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-08-10T10:00:00Z",
                        "timestamp_basis": (
                            "Approximate narrative order reconstructed by the agent; "
                            "not captured by an independent runtime."
                        ),
                        "run_id": "example-run",
                        "phase": "physical-inspection",
                        "action": "query",
                        "target": "public.payments",
                        "outcome": "candidate inputs found",
                        "evidence_references": ["schema"],
                        "gate": "read-only evidence only",
                        "telemetry": "self-declared",
                        "capture_mode": "retrospective_reconstruction",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(investigation), str(brief), str(trace)],
                capture_output=True,
                text=True,
            )

    def test_valid_evidence_package_passes(self) -> None:
        completed = self.run_validator(valid_package())

        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertIn("CHECK_INVESTIGATION=PASS", completed.stdout)

    def test_fact_without_evidence_fails(self) -> None:
        package = valid_package()
        package["claims"][0]["evidence_references"] = []

        completed = self.run_validator(package)

        self.assertEqual(1, completed.returncode)
        self.assertIn("fact requires evidence_references", completed.stdout)
        self.assertIn("CHECK_INVESTIGATION=FAIL", completed.stdout)

    def test_unknown_ontology_endpoint_fails(self) -> None:
        package = valid_package()
        package["ontology"]["relationships"][0]["object"] = "InventedMetric"

        completed = self.run_validator(package)

        self.assertEqual(1, completed.returncode)
        self.assertIn("unknown ontology node", completed.stdout)

    def test_trace_without_provenance_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            investigation = root / "investigation.json"
            brief = root / "technical-brief.md"
            trace = root / "trace.jsonl"
            investigation.write_text(json.dumps(valid_package()), encoding="utf-8")
            brief.write_text(VALID_BRIEF, encoding="utf-8")
            trace.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-08-10T10:00:00Z",
                        "run_id": "example-run",
                        "phase": "physical-inspection",
                        "action": "query",
                        "target": "public.payments",
                        "outcome": "candidate inputs found",
                        "evidence_references": ["schema"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), str(investigation), str(brief), str(trace)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("telemetry must be self-declared", completed.stdout)
        self.assertIn("capture_mode must be retrospective_reconstruction", completed.stdout)
        self.assertIn("CHECK_INVESTIGATION=FAIL", completed.stdout)

    def test_empty_trace_fails_when_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            investigation = root / "investigation.json"
            brief = root / "technical-brief.md"
            trace = root / "trace.jsonl"
            investigation.write_text(json.dumps(valid_package()), encoding="utf-8")
            brief.write_text(VALID_BRIEF, encoding="utf-8")
            trace.write_text("", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), str(investigation), str(brief), str(trace)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("trace must contain at least one JSON event", completed.stdout)

    def test_trace_with_unknown_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            root = Path(temp_directory)
            investigation = root / "investigation.json"
            brief = root / "technical-brief.md"
            trace = root / "trace.jsonl"
            investigation.write_text(json.dumps(valid_package()), encoding="utf-8")
            brief.write_text(VALID_BRIEF, encoding="utf-8")
            trace.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-08-10T10:00:00Z",
                        "timestamp_basis": "Approximate retrospective reconstruction.",
                        "run_id": "example-run",
                        "phase": "physical-inspection",
                        "action": "query",
                        "target": "public.payments",
                        "outcome": "candidate inputs found",
                        "evidence_references": ["missing-evidence"],
                        "gate": "read-only evidence only",
                        "telemetry": "self-declared",
                        "capture_mode": "retrospective_reconstruction",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), str(investigation), str(brief), str(trace)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("references unknown evidence: missing-evidence", completed.stdout)


if __name__ == "__main__":
    unittest.main()
