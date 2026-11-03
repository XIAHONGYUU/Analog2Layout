"""PDK fact-registry checks: authority and provenance, not DRC signoff."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "pdk/sky130/facts.json"


class PdkFactsTest(unittest.TestCase):
    def setUp(self):
        self.f = json.loads(FACTS.read_text())

    def test_minimum_facts_are_present(self):
        self.assertEqual(self.f["pdk"], "sky130A")
        self.assertGreaterEqual(len(self.f["rules"]), 10)
        self.assertEqual(self.f["rules"]["difftap_min_width_um"]["value"], 0.15)
        self.assertEqual(self.f["rules"]["difftap_min_space_um"]["value"], 0.27)
        self.assertEqual(self.f["rules"]["dnwell_min_space_um"]["value"], 6.3)

    def test_ring_is_not_a_pdk_fact(self):
        ring = self.f["ring"]
        self.assertFalse(ring["pdk_defined"])
        self.assertIn("No.", ring["answer"])
        self.assertIn("1.0", ring["answer"])
        self.assertIn("difftap_min_width_um", ring["applicable_min_rules"])

    def test_every_fact_has_rule_and_source_line(self):
        for key, rec in self.f["rules"].items():
            with self.subTest(key=key):
                self.assertTrue(rec["drc_rule"])
                self.assertIsInstance(rec["source_line"], int)
                self.assertGreater(rec["source_line"], 0)
                self.assertGreater(rec["value"], 0)


if __name__ == "__main__":
    unittest.main()
