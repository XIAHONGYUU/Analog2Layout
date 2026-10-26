import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "classa_opamp" / "opamp.sp"
SIZED = ROOT / "examples" / "classa_opamp" / "opamp.sized.sp"


class ClassAReviewTests(unittest.TestCase):
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

    def test_sized_netlist_uses_unit_w_and_m(self):
        netlist = parse_file(SIZED)
        self.assertEqual(len(netlist.devices), 17)
        devices = netlist.device_by_name()
        self.assertEqual(devices["M14"].params["w"], "18u")
        self.assertEqual(devices["M14"].params["m"], "100")
        self.assertEqual(devices["M8"].params["w"], "9u")
        self.assertEqual(devices["M8"].params["m"], "12")

    def test_fixed_mom_cap_geometry(self):
        netlist = parse_file(SIZED)
        report = estimate_area(netlist, self.rules)
        cap = next(d for d in report.devices if d.name == "C1_CC")
        self.assertAlmostEqual(cap.area_core_um2, 50.0)
        self.assertAlmostEqual(cap.area_total_um2, 50.0)
        self.assertAlmostEqual(cap.w_layout_um, 5.0)
        self.assertAlmostEqual(cap.h_layout_um, 10.0)


if __name__ == "__main__":
    unittest.main()
