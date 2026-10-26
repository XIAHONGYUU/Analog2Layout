import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "classab_opamp" / "opamp.sp"


class ClassAbReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())
        cls.netlist = parse_file(NETLIST)
        cls.report = estimate_area(cls.netlist, cls.rules)

    def test_real_schematic_netlist_parses(self):
        self.assertEqual(len(self.netlist.devices), 17)
        self.assertEqual(sum(1 for d in self.netlist.devices if d.kind == "mos"), 16)
        self.assertEqual(sum(1 for d in self.netlist.devices if d.kind == "cap"), 1)

    def test_raw_names_need_role_map(self):
        self.assertEqual(self.report.summary["role_sources"]["unknown"], 16)
        self.assertFalse(self.report.summary["all_roles_known"])


if __name__ == "__main__":
    unittest.main()
