import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.netlist import parse_file, parse_text
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent


class AreaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())

    def test_two_stage_area(self):
        netlist = parse_file(ROOT / "examples" / "two_stage" / "two_stage.sp")
        report = estimate_area(netlist, self.rules)
        self.assertGreater(report.summary["area_block_with_dummy_um2"], 0)
        self.assertGreater(
            report.summary["area_block_with_dummy_um2"],
            report.summary["area_block_no_dummy_um2"],
        )
        self.assertLess(report.summary["area_low_um2"], report.summary["area_high_um2"])

        groups = {group.key: group for group in report.groups}
        self.assertIn("DP", groups)
        self.assertEqual(groups["DP"].dummy_count, 2)
        self.assertEqual(groups["DP"].role, "input_pair")

        devices = {device.name: device for device in report.devices}
        self.assertGreater(devices["M1"].area_total_um2, 0)
        self.assertGreater(devices["C1"].area_total_um2, 0)
        self.assertAlmostEqual(devices["C1"].area_core_um2, 1000.0, places=3)

    def test_area_hierarchy_and_provenance(self):
        netlist = parse_file(ROOT / "examples" / "two_stage" / "two_stage.sp")
        report = estimate_area(netlist, self.rules)
        summary = report.summary
        self.assertLess(summary["area_core_um2"], summary["area_active_um2"])
        self.assertLess(summary["area_active_um2"], summary["area_matched_um2"])
        self.assertLess(summary["area_matched_um2"], summary["area_block_um2"])
        self.assertLess(summary["area_block_um2"], summary["area_envelope_um2"])
        self.assertAlmostEqual(
            summary["area_envelope_um2"],
            summary["area_block_um2"] + summary["area_reserved_um2"],
            places=1,
        )
        self.assertEqual(summary["role_sources"]["explicit"], 10)
        self.assertTrue(summary["all_roles_explicit"])
        self.assertEqual(report.rules_owner, "analog design engineer")

    def test_name_fallback_is_only_a_suggestion(self):
        text = ".subckt x d g s b\nM1_DP d g s b nmos w=2u l=0.5u\n.ends x\n"
        netlist = parse_text(text, name="x")
        report = estimate_area(netlist, self.rules)
        self.assertEqual(report.devices[0].role, "input_pair")
        self.assertEqual(report.devices[0].role_source, "name")
        self.assertEqual(report.summary["role_sources"]["name"], 1)
        self.assertFalse(report.summary["all_roles_explicit"])
        self.assertTrue(any("confirm it with the analog owner" in warning for warning in report.warnings))

    def test_area_gate_three_values(self):
        netlist = parse_file(ROOT / "examples" / "two_stage" / "two_stage.sp")
        passed = estimate_area(netlist, self.rules, area_budget_um2=5000.0)
        self.assertEqual(passed.summary["area_gate"]["status"], "PASS")
        self.assertGreater(passed.summary["area_gate"]["headroom_um2"], 0)
        self.assertEqual(passed.summary["area_gate"]["shortfall_um2"], 0)

        rejected = estimate_area(netlist, self.rules, area_budget_um2=1000.0)
        self.assertEqual(rejected.summary["area_gate"]["status"], "REJECT")
        self.assertGreater(rejected.summary["area_gate"]["shortfall_um2"], 0)

        uncertain = estimate_area(netlist, self.rules, area_budget_um2=3000.0)
        self.assertEqual(uncertain.summary["area_gate"]["status"], "UNCERTAIN")
        self.assertGreater(uncertain.summary["area_gate"]["overlap_um2"], 0)

        unset = estimate_area(netlist, self.rules)
        self.assertEqual(unset.summary["area_gate"]["status"], "UNSET")

    def test_total_width_convention(self):
        text = ".subckt x d g s b\nM1 d g s b nmos w=20u l=1u nf=4 role=output_stage\n.ends x\n"
        netlist = parse_text(text, name="x")
        per_finger = estimate_area(netlist, self.rules)
        # A different rule object is not needed: width_convention is read from
        # the rule pack, so validate the helper directly.
        self.assertAlmostEqual(netlist.devices[0].total_width_um("per_finger"), 80.0)
        self.assertAlmostEqual(netlist.devices[0].total_width_um("total"), 20.0)
        self.assertGreater(per_finger.summary["area_block_with_dummy_um2"], 0)

    def test_missing_geometry_is_reported(self):
        text = ".subckt x d g s b\nM1 d g s b nmos role=input_pair\n.ends x\n"
        netlist = parse_text(text, name="x")
        report = estimate_area(netlist, self.rules)
        self.assertTrue(any("W must be > 0" in warning or "missing" in warning for warning in report.warnings))


if __name__ == "__main__":
    unittest.main()
