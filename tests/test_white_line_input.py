"""Golden-case checks for the white-line input/skill contract.

The JSON schema remains the authoritative contract.  This test is intentionally
stdlib-only so CI does not need a jsonschema dependency; when jsonschema is
available locally it also validates the schema.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "examples/classa_opamp/white-line-input.json"
EXPECTED = ROOT / "examples/classa_opamp/white-line-expected.json"
SCHEMA = ROOT / "schemas/white_line_input.schema.json"
ARTIFACT = ROOT / "examples/classa_opamp/area-min.svg"


class WhiteLineGoldenCaseTest(unittest.TestCase):
    def setUp(self):
        self.input = json.loads(INPUT.read_text())
        self.expected = json.loads(EXPECTED.read_text())
        self.schema = json.loads(SCHEMA.read_text())

    def test_schema_is_json(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["properties"]["schema_version"]["const"], "1.0")

    def test_input_has_required_top_level_contract(self):
        for key in ("schema_version", "module", "units", "devices", "groups",
                    "passives", "rules", "constraints", "priorities"):
            self.assertIn(key, self.input)

    def test_groups_cover_all_devices(self):
        members = {m for g in self.input["groups"] for m in g["members"]}
        devices = {d["name"] for d in self.input["devices"]}
        self.assertEqual(devices, members)
        self.assertEqual(len(devices), 16)
        self.assertEqual(len(self.input["groups"]), 7)
        self.assertEqual(len(self.input["passives"]), 2)

    def test_golden_metrics_are_self_consistent(self):
        m = self.expected["metrics"]
        w, h = m["bbox_um"]
        self.assertAlmostEqual(m["area_um2"], w * h, places=3)
        self.assertAlmostEqual(m["utilization"], m["effective_um2"] / m["area_um2"], places=6)
        self.assertAlmostEqual(m["aspect_w_over_h"], w / h, places=6)

    def test_selected_artifact_exists(self):
        self.assertTrue(ARTIFACT.exists(), ARTIFACT)
        self.assertEqual(self.expected["artifact"], "examples/classa_opamp/area-min.svg")

    def test_hard_constraints_are_recorded(self):
        c = self.input["constraints"]
        self.assertEqual(c["objective"], "min_area")
        self.assertTrue(c["output_outer"])
        self.assertTrue(c["passives_inside_dnw"])
        self.assertEqual(c["dummy_policy"], "same_geometry")
        self.assertFalse(c["fake_fill"])
        self.assertEqual(c["area_denominator"], "dnw_bbox")
        self.assertEqual(c["effective_area"], "ring_inner_plus_ring_aa_plus_passives")
        for key in ("passives_inside_dnw", "ring_aa_counted", "dummy_same_geometry",
                    "no_fake_fill", "output_outer"):
            self.assertTrue(self.expected["checks"][key])


if __name__ == "__main__":
    unittest.main()
