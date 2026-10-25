import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NETLIST = ROOT / "examples" / "two_stage" / "two_stage.sp"


class CliTests(unittest.TestCase):
    def test_build_writes_bundle(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            out = Path(directory) / "bundle"
            result = subprocess.run(
                [sys.executable, "-m", "a2l", "build", str(NETLIST), "--out", str(out), "--quiet"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in (
                "area_report.json",
                "area_report.md",
                "floorplan.json",
                "floorplan.svg",
                "layout_delta.json",
                "HANDOFF.md",
                "index.html",
            ):
                self.assertTrue((out / name).exists(), name)

    def test_validate(self):
        result = subprocess.run(
            [sys.executable, "-m", "a2l", "validate", str(NETLIST), "--quiet"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_require_known_roles(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "a2l",
                "validate",
                str(NETLIST),
                "--require-known-roles",
                "--quiet",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            fallback = Path(directory) / "fallback.sp"
            fallback.write_text(
                ".subckt x d g s b\nM1 d g s b nmos w=2u l=0.5u\n.ends x\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "a2l",
                    "validate",
                    str(fallback),
                    "--require-known-roles",
                    "--quiet",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("role is unknown", result.stderr)

    def test_fail_on_gate(self):
        passed = subprocess.run(
            [
                sys.executable,
                "-m",
                "a2l",
                "analyze",
                str(NETLIST),
                "--area-budget-mm2",
                "0.005",
                "--fail-on-gate",
                "--quiet",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(passed.returncode, 0, passed.stderr)

        rejected = subprocess.run(
            [
                sys.executable,
                "-m",
                "a2l",
                "analyze",
                str(NETLIST),
                "--area-budget-mm2",
                "0.001",
                "--fail-on-gate",
                "--quiet",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("area gate is REJECT", rejected.stderr)

    def test_compare(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "a2l",
                "compare",
                str(NETLIST),
                str(ROOT / "examples" / "ota5_cascode" / "ota5_cascode.sp"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Architecture area comparison", result.stdout)


if __name__ == "__main__":
    unittest.main()
