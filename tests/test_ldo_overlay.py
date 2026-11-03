"""Integrity checks for the imported NetlistLabel LDO overlay fixture."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "examples/sky130_ldo_01v8/netlistlabel-overlay"
RAW = ROOT / "examples/sky130_ldo_01v8/ldo.sp"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LdoOverlayTest(unittest.TestCase):
    def setUp(self):
        self.prov = json.loads((OVERLAY / "provenance.json").read_text())

    def test_raw_source_hash_matches(self):
        self.assertEqual(sha(RAW), self.prov["raw_netlist"]["sha256"])

    def test_provenance_file_hashes_match(self):
        for rel, expected in self.prov["files"].items():
            self.assertEqual(sha(OVERLAY / rel), expected, rel)

    def test_checksums_cover_imported_files(self):
        listed = {}
        for line in (OVERLAY / "checksums.sha256").read_text().splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            listed[rel] = digest
        for rel, digest in listed.items():
            self.assertEqual(sha(OVERLAY / rel), digest, rel)

    def test_overlay_shape_and_status(self):
        text = (OVERLAY / "ldo.annotated.sp").read_text()
        self.assertEqual(len(re.findall(r"^XM", text, re.M)), 41)
        self.assertEqual(len(re.findall(r"^(?:XR|XC)", text, re.M)), 5)
        self.assertIn("PROPOSAL, NOT APPROVED", text)
        self.assertNotIn("/home/zuoky", text)
        self.assertTrue((OVERLAY / "annotation.json").exists())
        self.assertTrue((OVERLAY / "eval/eval.md").exists())

    def test_review_is_explicitly_sampled(self):
        self.assertIn("sampled human review", self.prov["review"]["status"])
        eval_text = (OVERLAY / "eval/eval.md").read_text()
        self.assertIn("not a global accuracy claim", eval_text)

    def test_no_personal_path_outside_provenance_note(self):
        for p in OVERLAY.rglob("*"):
            if p.is_file() and p.name not in {"provenance.json"}:
                self.assertNotIn("/home/zuoky", p.read_text(errors="ignore"), str(p))


if __name__ == "__main__":
    unittest.main()
