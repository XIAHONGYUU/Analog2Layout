import unittest
from pathlib import Path

from a2l.netlist import parse_file, parse_text

ROOT = Path(__file__).resolve().parent.parent


class NetlistTests(unittest.TestCase):
    def test_two_stage_example(self):
        netlist = parse_file(ROOT / "examples" / "two_stage" / "two_stage.sp")
        self.assertEqual(len(netlist.devices), 10)
        devices = netlist.device_by_name()
        self.assertIn("M1", devices)
        self.assertEqual(devices["M1"].role, "input_pair")
        self.assertEqual(devices["M1"].match, "DP")
        self.assertEqual(devices["M1"].group, "IN")
        self.assertEqual(devices["M1"].nf, 4)
        self.assertAlmostEqual(devices["M1"].total_width_um(), 20.0)
        self.assertEqual(devices["C1"].kind, "cap")
        self.assertAlmostEqual(devices["C1"].c_pf, 1.5)

    def test_spectre_style(self):
        text = """
.subckt x d g s b
M1 (d g s b) nmos w=2u l=0.5u nf=2 role=input_pair
.ends x
"""
        netlist = parse_text(text, name="x")
        self.assertEqual(len(netlist.devices), 1)
        device = netlist.devices[0]
        self.assertEqual(device.nodes, ["d", "g", "s", "b"])
        self.assertEqual(device.model, "nmos")
        self.assertEqual(device.role, "input_pair")

    def test_continuation_and_name_fallback(self):
        text = """
.subckt y d g s b
M1 d g s b nmos w=2u
+ l=0.5u nf=1
.ends y
"""
        netlist = parse_text(text, name="y")
        self.assertAlmostEqual(netlist.devices[0].l_um, 0.5)
        # No role= and no role-bearing name -> unknown.
        self.assertEqual(netlist.devices[0].role, "unknown")

        text2 = ".subckt z d g s b\nM1_DP d g s b nmos w=2u l=0.5u\n.ends z\n"
        netlist2 = parse_text(text2, name="z")
        self.assertEqual(netlist2.devices[0].role, "input_pair")
        self.assertEqual(netlist2.devices[0].role_source, "name")

    def test_capacitor_forms(self):
        netlist = parse_text(
            ".subckt c a b\nC1 a b 2p role=decap\nC2 a b c=1.5p\n.ends c\n",
            name="c",
        )
        self.assertAlmostEqual(netlist.devices[0].c_pf, 2.0)
        self.assertAlmostEqual(netlist.devices[1].c_pf, 1.5)


if __name__ == "__main__":
    unittest.main()
