"""Checks for the LDO white-line input generated from the imported overlay."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "examples/sky130_ldo_01v8/white-line-input.json"
OVERLAY = ROOT / "examples/sky130_ldo_01v8/netlistlabel-overlay/ldo.annotated.sp"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LdoWhiteLineInputTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(INPUT.read_text())

    def test_counts(self):
        self.assertEqual(len(self.data["devices"]), 41)
        self.assertEqual(len(self.data["passives"]), 5)
        self.assertEqual(len(self.data["blackboxes"]), 2)
        self.assertEqual(len(self.data["groups"]), 9)

    def test_groups_cover_all_members(self):
        members = {m for g in self.data["groups"] for m in g["members"]}
        refs = {d["name"] for d in self.data["devices"]}
        refs |= {p["name"] for p in self.data["passives"]}
        refs |= {b["name"] for b in self.data["blackboxes"]}
        self.assertEqual(members, refs)

    def test_overlay_hash_and_proposal_status(self):
        self.assertEqual(self.data["semantic_source"]["sha256"], sha(OVERLAY))
        self.assertIn("PROPOSAL", self.data["semantic_source"]["status"])
        self.assertIn("sampled human review", self.data["semantic_source"]["review"])

    def test_unknowns_are_visible(self):
        self.assertTrue(all(d["sd_mode"] == "unknown" for d in self.data["devices"]))
        self.assertTrue(all(b["status"] == "unknown" for b in self.data["blackboxes"]))
        unreviewed = {p["name"] for p in self.data["passives"] if p["review_status"] != "sampled_reviewed"}
        self.assertEqual(unreviewed, {"XC3", "XR6"})
        self.assertTrue(any("sd_mode" in u for u in self.data["unknowns"]))

    def test_schema_validation_if_available(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema not installed")
        schema = json.loads((ROOT / "schemas/white_line_input.schema.json").read_text())
        errs = list(Draft202012Validator(schema).iter_errors(self.data))
        self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main()
