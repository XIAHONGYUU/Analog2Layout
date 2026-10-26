import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "sky130_ldo_01v8" / "ldo.sp"


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


if __name__ == "__main__":
    unittest.main()
