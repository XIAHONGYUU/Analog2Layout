import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.floorplan import build_floorplan
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "sky130_ldo_01v8" / "ldo.sp"
ANNOTATED = ROOT / "examples" / "sky130_ldo_01v8" / "ldo.annotated.sp"


class LdoCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())
        cls.netlist = parse_file(NETLIST)
        cls.report = estimate_area(cls.netlist, cls.rules)

    def test_xm_devices_are_parsed_as_mos(self):
        self.assertEqual(len(self.netlist.devices), 41)
        self.assertEqual(sum(1 for d in self.netlist.devices if d.kind == "mos"), 41)
        devices = self.netlist.device_by_name()
        self.assertIn("XM61", devices)
        self.assertEqual(devices["XM61"].params.get("m"), "1000")

    def test_real_ldo_names_are_not_semantic(self):
        self.assertEqual(self.report.summary["role_sources"]["unknown"], 41)
        self.assertFalse(self.report.summary["all_roles_known"])

    def test_area_is_positive_but_undercounted(self):
        self.assertGreater(self.report.summary["area_block_um2"], 0)

    def test_annotated_role_proposal(self):
        netlist = parse_file(ANNOTATED)
        report = estimate_area(netlist, self.rules)
        self.assertEqual(len(netlist.devices), 41)
        self.assertEqual(report.summary["group_count"], 14)
        self.assertTrue(report.summary["all_roles_known"])
        self.assertEqual(report.summary["role_sources"]["explicit"], 41)
        self.assertEqual(netlist.device_by_name()["XM61"].role, "output_stage")

    def test_power_device_is_folded_in_floorplan(self):
        netlist = parse_file(ANNOTATED)
        report = estimate_area(netlist, self.rules)
        fp = build_floorplan("ldo.annotated", report, self.rules)
        pass_dev = next(
            device
            for group in fp.groups
            for device in group.devices
            if device.name == "XM61"
        )
        self.assertGreater(pass_dev.fold, 1)
        self.assertLessEqual(pass_dev.w, 100.01)


if __name__ == "__main__":
    unittest.main()
