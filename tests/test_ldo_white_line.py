"""Checks for the deterministic device-level LDO white-line compiler."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "examples/sky130_ldo_01v8/white-line-manifest.json"
SVG = ROOT / "examples/sky130_ldo_01v8/white-line.svg"
PNG = ROOT / "examples/sky130_ldo_01v8/white-line.png"


class LdoWhiteLineTest(unittest.TestCase):
    def setUp(self):
        self.m = json.loads(MANIFEST.read_text())

    def test_outputs_exist(self):
        self.assertTrue(MANIFEST.exists())
        self.assertTrue(SVG.exists())
        self.assertTrue(PNG.exists())

    def test_device_and_hierarchy_counts(self):
        self.assertEqual(len(self.m["devices"]), 41)
        self.assertEqual(len(self.m["device_clusters"]), 34)
        self.assertEqual(len(self.m["passive_blocks"]), 5)
        self.assertEqual(len(self.m["blackboxes"]), 2)
        self.assertEqual(len(self.m["blocks"]), 20)
        self.assertEqual(self.m["dnw2"]["contains"], ["XM61", "guard_ring"])

    def test_metrics_self_consistent(self):
        w, h = self.m["bbox_um"]
        self.assertAlmostEqual(self.m["area_um2"], w * h, places=3)
        self.assertAlmostEqual(self.m["utilization"], self.m["effective_um2"] / self.m["area_um2"], places=6)
        self.assertGreater(self.m["effective_um2"], 0)
        self.assertLess(self.m["utilization"], 1)

    def test_ring_audit_is_explicit(self):
        r = self.m["ring_audit"]
        self.assertEqual(r["mos_width_um"], 1.0)
        self.assertEqual(r["gap_um"], 0.8)
        self.assertEqual(r["dnw_margin_um"], 3.0)
        self.assertIn("not a ring", r["note"])

    def test_dnw_geometry(self):
        self.assertEqual(self.m["checks"]["dnw_gap_outer"], 8.0)
        self.assertTrue(self.m["checks_geometry"]["block_overlap"] is False)
        self.assertTrue(self.m["checks_geometry"]["dnw1_contains_blocks"])
        self.assertTrue(self.m["checks"]["passives_inside_dnw1"])
        self.assertTrue(self.m["checks"]["x1_x2_inside_dnw1"])

    def test_device_clusters_have_rows_cols_and_sequences(self):
        for d in self.m["device_clusters"]:
            self.assertGreaterEqual(d["rows"], 1)
            self.assertGreaterEqual(d["cols"], 1)
            self.assertGreaterEqual(d["fingers"], 1)
            self.assertGreater(d["w"], 0)
            self.assertGreater(d["h"], 0)
            self.assertEqual(len(d["sequence"]), d["fingers"])
            if d["dummy_cols"]:
                self.assertTrue(any(n in d["members"] for n in d["sequence"]))


if __name__ == "__main__":
    unittest.main()
