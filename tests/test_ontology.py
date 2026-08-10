"""Contract tests for the evidence-aware ontology surface."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from transactco.domain import explain_concept, load_ontology, validate_ontology


class OntologyTests(unittest.TestCase):
    def test_default_ontology_is_structurally_valid(self) -> None:
        ontology = load_ontology()

        self.assertEqual([], validate_ontology(ontology))
        self.assertEqual("pending human review", ontology["status"])

    def test_revenue_exposes_decision_boundary(self) -> None:
        result = explain_concept(load_ontology(), "revenue")

        self.assertEqual("unresolved", result["status"])
        self.assertEqual("blocked_by_business_decisions", result["answerability"])
        self.assertEqual("Finance owner", result["owner"])
        self.assertIn("Payment.amount", result["candidate_inputs"])
        self.assertGreaterEqual(len(result["required_decisions"]), 4)

    def test_cli_json_output_is_agent_readable(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "transactco.cli",
                "ontology",
                "explain",
                "Revenue",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual("Revenue", payload["name"])
        self.assertEqual("blocked_by_business_decisions", payload["answerability"])

    def test_invalid_relationship_endpoint_is_rejected(self) -> None:
        ontology = load_ontology()
        ontology["relationships"][0]["object"] = "MissingEntity"

        errors = validate_ontology(ontology)

        self.assertTrue(any("MissingEntity" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
