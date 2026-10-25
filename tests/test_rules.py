import json
import tempfile
import unittest
from pathlib import Path

from a2l.rules import RuleError, default_rules_path, load_rules

ROOT = Path(__file__).resolve().parent.parent


class RuleTests(unittest.TestCase):
    def test_bundled_pack_has_owner(self):
        rules = load_rules(default_rules_path())
        self.assertEqual(rules.owner, "analog design engineer")
        self.assertTrue(rules.approval)

    def test_missing_owner_is_rejected(self):
        data = json.loads((ROOT / "rules" / "generic_180.json").read_text(encoding="utf-8"))
        data.pop("owner")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "no_owner.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(RuleError):
                load_rules(path)

    def test_missing_approval_is_rejected(self):
        data = json.loads((ROOT / "rules" / "generic_180.json").read_text(encoding="utf-8"))
        data.pop("approval")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "no_approval.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(RuleError):
                load_rules(path)


if __name__ == "__main__":
    unittest.main()
