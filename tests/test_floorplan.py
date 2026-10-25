import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from a2l.area import estimate_area
from a2l.floorplan import build_floorplan
from a2l.netlist import parse_file
from a2l.rules import default_rules_path, load_rules
from a2l.svg import render_floorplan_svg

ROOT = Path(__file__).resolve().parent.parent


class FloorplanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules(default_rules_path())
        cls.netlist = parse_file(ROOT / "examples" / "two_stage" / "two_stage.sp")
        cls.report = estimate_area(cls.netlist, cls.rules)
        cls.fp = build_floorplan("two_stage", cls.report, cls.rules)

    def test_no_device_overlap(self):
        devices = self.fp.devices
        for index, first in enumerate(devices):
            for second in devices[index + 1 :]:
                overlap_x = max(
                    0.0,
                    min(first.x + first.w, second.x + second.w) - max(first.x, second.x),
                )
                overlap_y = max(
                    0.0,
                    min(first.y + first.h, second.y + second.h) - max(first.y, second.y),
                )
                self.assertFalse(
                    overlap_x > 1e-6 and overlap_y > 1e-6,
                    f"{first.name} overlaps {second.name}",
                )

    def test_devices_inside_canvas(self):
        for device in self.fp.devices:
            self.assertGreaterEqual(device.x, 0.0)
            self.assertGreaterEqual(device.y, 0.0)
            self.assertLessEqual(device.x + device.w, self.fp.width + 1e-6)
            self.assertLessEqual(device.y + device.h, self.fp.height + 1e-6)

    def test_input_pair_straddles_symmetry_axis(self):
        pair = next(group for group in self.fp.groups if group.role == "input_pair")
        left = next(device for device in pair.devices if device.name == "M1")
        right = next(device for device in pair.devices if device.name == "M2")
        self.assertLess(left.x + left.w, self.fp.symmetry_x)
        self.assertGreater(right.x, self.fp.symmetry_x)

    def test_proposed_dummies_and_svg(self):
        proposed = [device for device in self.fp.devices if device.proposed]
        self.assertTrue(proposed)
        svg = render_floorplan_svg(self.fp)
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("M1", svg)
        self.assertIn("SYM AXIS", svg)
        self.assertIn("PEX-FIX RESERVE", svg)

    def test_shape_and_arrangement_stats(self):
        stats = self.fp.stats
        self.assertGreater(stats["block_width_um"], 0)
        self.assertGreater(stats["block_height_um"], 0)
        self.assertGreater(stats["aspect_ratio"], 0)
        self.assertLessEqual(stats["squareness"], 1.0)
        self.assertIn(stats["orientation"], ("landscape", "portrait", "square-ish"))
        self.assertEqual(stats["rows"], len(self.fp.bands))
        self.assertIn("arrangement", stats)
        self.assertGreaterEqual(stats["core_utilization"], 0.0)

    def test_json_serializable(self):
        data = self.fp.to_dict()
        self.assertIn("groups", data)
        self.assertIn("devices", data)
        self.assertIn("reserve", data)


if __name__ == "__main__":
    unittest.main()
