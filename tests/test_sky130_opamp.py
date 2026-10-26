import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "sky130_two_stage_opamp" / "opamp.sp"


class Sky130OpampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())
        cls.netlist = parse_file(NETLIST)
        cls.report = estimate_area(cls.netlist, cls.rules)

    def test_target_has_real_core_and_aux_devices(self):
        devices = self.netlist.device_by_name()
        self.assertEqual(len(self.netlist.devices), 11)
        self.assertEqual(sum(1 for d in self.netlist.devices if d.kind == "mos"), 10)
        self.assertEqual(devices["M1_DP"].role, "input_pair")
        self.assertEqual(devices["M8_BIAS"].role, "bias")
        self.assertEqual(devices["M9_EN"].role, "enable_switch")
        self.assertEqual(devices["M10_EN_PD"].role, "enable_switch")

    def test_name_only_roles_and_groups(self):
        devices = self.netlist.device_by_name()
        self.assertEqual(devices["M1_DP"].role_source, "name")
        self.assertEqual(devices["M1_DP"].match, "DP")
        self.assertEqual(devices["M3_CM"].match, "CM")
        self.assertEqual(devices["M6_OUT"].group, "OUT")
        self.assertTrue(self.report.summary["all_roles_known"])
        self.assertEqual(self.report.summary["role_sources"]["name"], 11)
        self.assertEqual(self.report.summary["role_sources"]["unknown"], 0)

    def test_area_and_floorplan_inputs(self):
        self.assertGreater(self.report.summary["area_block_um2"], 0)
        self.assertGreater(self.report.summary["area_dummy_um2"], 0)
        self.assertEqual(self.report.summary["group_count"], 7)
        self.assertGreater(self.report.summary["area_envelope_um2"], self.report.summary["area_block_um2"])


if __name__ == "__main__":
    unittest.main()
