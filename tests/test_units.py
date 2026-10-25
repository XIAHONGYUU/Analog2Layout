import unittest

from a2l.units import parse_cap_pf, parse_eng, parse_length_um, parse_positive_int


class UnitTests(unittest.TestCase):
    def test_lengths(self):
        self.assertAlmostEqual(parse_length_um("10u"), 10.0)
        self.assertAlmostEqual(parse_length_um("500n"), 0.5)
        self.assertAlmostEqual(parse_length_um("1.5um"), 1.5)
        self.assertAlmostEqual(parse_length_um("0.18"), 0.18)

    def test_capacitance(self):
        self.assertAlmostEqual(parse_cap_pf("1.5p"), 1.5)
        self.assertAlmostEqual(parse_cap_pf("1500f"), 1.5)
        self.assertAlmostEqual(parse_cap_pf("2pF"), 2.0)

    def test_engineering(self):
        self.assertAlmostEqual(parse_eng("2.2k"), 2200.0)
        self.assertAlmostEqual(parse_eng("1meg"), 1e6)
        self.assertAlmostEqual(parse_eng("1e-6"), 1e-6)

    def test_integer(self):
        self.assertEqual(parse_positive_int("4"), 4)
        with self.assertRaises(ValueError):
            parse_positive_int("2.5")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            parse_eng("not-a-number")


if __name__ == "__main__":
    unittest.main()
