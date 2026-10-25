import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "name_only_ota" / "ota_named.sp"


class NameOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())
        cls.netlist = parse_file(NETLIST)
        cls.report = estimate_area(cls.netlist, cls.rules)

    def test_names_are_the_primary_source(self):
        devices = self.netlist.device_by_name()
        self.assertEqual(devices["M1_DP"].role, "input_pair")
        self.assertEqual(devices["M1_DP"].role_source, "name")
        self.assertEqual(devices["M1_DP"].match, "DP")
        self.assertEqual(devices["M3_CM"].match, "CM")
        self.assertEqual(devices["M6_OUT"].group, "OUT")

    def test_all_roles_known(self):
        self.assertTrue(self.report.summary["all_roles_known"])
        self.assertEqual(self.report.summary["role_sources"]["name"], 10)
        self.assertEqual(self.report.summary["role_sources"]["unknown"], 0)

    def test_matching_groups_and_area(self):
        groups = {group.key: group for group in self.report.groups}
        self.assertIn("DP", groups)
        self.assertIn("CM", groups)
        self.assertIn("OUT", groups)
        self.assertEqual(groups["DP"].dummy_count, 2)
        self.assertGreater(self.report.summary["area_block_um2"], 0)


if __name__ == "__main__":
    unittest.main()
