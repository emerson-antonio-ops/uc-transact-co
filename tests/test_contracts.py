from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from transactco.cli import _format_utc
from transactco.defects import ALL_DEFECTS, DEFECT_REGISTRY, SCENARIOS
from transactco.score import _family


class DefectContractTests(unittest.TestCase):
    def test_exactly_fourteen_named_defects_are_registered(self) -> None:
        self.assertEqual(14, len(ALL_DEFECTS))
        self.assertEqual(set(ALL_DEFECTS), set(DEFECT_REGISTRY))

    def test_all_scenario_contains_each_defect_once(self) -> None:
        self.assertEqual(ALL_DEFECTS, SCENARIOS["all"])
        self.assertEqual(len(SCENARIOS["all"]), len(set(SCENARIOS["all"])))

    def test_every_scenario_references_registered_defects(self) -> None:
        registered = set(ALL_DEFECTS)
        for scenario, members in SCENARIOS.items():
            with self.subTest(scenario=scenario):
                self.assertTrue(members)
                self.assertLessEqual(set(members), registered)

    def test_schema_drift_runs_last(self) -> None:
        self.assertEqual("schema_drift", ALL_DEFECTS[-1])

    def test_cascade_symptoms_score_as_one_family(self) -> None:
        self.assertEqual(
            "multi_failure_cascade",
            _family("multi_failure_cascade/duplicate_payment"),
        )

    def test_detector_names_are_normalized(self) -> None:
        self.assertEqual("negative_price", _family("Negative Price"))
        self.assertEqual("late_arrival", _family("late-arrival"))

    def test_status_timestamps_use_one_explicit_utc_clock(self) -> None:
        local_time = datetime(
            2026,
            8,
            10,
            13,
            12,
            tzinfo=timezone(timedelta(hours=-3)),
        )
        self.assertEqual("2026-08-10 16:12 UTC", _format_utc(local_time))


if __name__ == "__main__":
    unittest.main()
