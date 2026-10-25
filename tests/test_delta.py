import unittest
from pathlib import Path

from a2l.area import estimate_area
from a2l.delta import plan_layout_delta
from a2l.floorplan import build_floorplan
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent


class DeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())
        cls.netlist = parse_file(ROOT / "examples" / "two_stage" / "two_stage.sp")
        cls.report = estimate_area(cls.netlist, cls.rules)
        cls.fp = build_floorplan("two_stage", cls.report, cls.rules)
        cls.delta = plan_layout_delta(cls.report, cls.fp, cls.rules)

    def test_expected_kinds(self):
        kinds = {item.kind for item in self.delta.items}
        self.assertIn("dummy", kinds)
        self.assertIn("decap", kinds)
        self.assertIn("reserve", kinds)
        self.assertIn("guard_ring", kinds)
        self.assertIn("dummy_logic", kinds)

    def test_owners_and_status(self):
        owners = {item.owner for item in self.delta.items}
        self.assertIn("analog", owners)
        self.assertIn("layout", owners)
        self.assertTrue(all(item.status == "proposed" for item in self.delta.items))

    def test_pex_scope(self):
        self.assertTrue(any("input" in scope.lower() for scope in self.delta.pex_resim_scope))
        self.assertTrue(any("stability" in scope.lower() or "phase" in scope.lower() for scope in self.delta.pex_resim_scope))

    def test_json(self):
        data = self.delta.to_dict()
        self.assertEqual(data["summary"]["item_count"], len(self.delta.items))
        self.assertGreater(data["summary"]["area_delta_um2"], 0)

    def test_reserve_check_is_explicit(self):
        # The demo intentionally proposes a 2 pF decap, which is larger than
        # the 8% reserve. The report must say so rather than hide it.
        self.assertFalse(self.delta.summary["reserve_sufficient"])
        self.assertGreater(self.delta.summary["reserve_shortfall_um2"], 0)
        self.assertTrue(any("exceeds the PEX-fix reserve" in note for note in self.delta.notes))


if __name__ == "__main__":
    unittest.main()
