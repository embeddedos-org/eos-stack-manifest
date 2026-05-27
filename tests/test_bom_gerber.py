"""
tests/test_bom_gerber.py
Real unit tests for eFab BOM generator and Gerber validator.
Run: python3 -m pytest tests/ -v
"""

import sys
import os
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from efab.bom import BOMGenerator, Component, BOMResult
from efab.gerber import (
    GerberParser, ManufacturingValidator, ManufacturingPackage,
    GerberLayer, GerberStats
)


# ─── BOM Tests ────────────────────────────────────────────────────────────────

class TestBOMGenerator(unittest.TestCase):

    def setUp(self):
        self.gen = BOMGenerator()

    def _make_components(self):
        return [
            Component("R1",  "10k",   "Resistor_SMD:R_0402", lcsc="C25741"),
            Component("R2",  "10k",   "Resistor_SMD:R_0402", lcsc="C25741"),
            Component("R3",  "100k",  "Resistor_SMD:R_0402", lcsc="C25752"),
            Component("C1",  "100nF", "Capacitor_SMD:C_0402", lcsc="C1525"),
            Component("C2",  "100nF", "Capacitor_SMD:C_0402", lcsc="C1525"),
            Component("U1",  "STM32F411", "LQFP-64", mpn="STM32F411CEU6"),
            Component("LED1","DNP",   "LED_SMD:LED_0402", dnp=True),
        ]

    def test_aggregates_same_value_footprint(self):
        """R1 and R2 (same 10k/R_0402) should be merged into one BOM line."""
        result = self.gen.generate(self._make_components())
        refs_per_line = {line.value: line.refs for line in result.lines}
        self.assertIn("10k", refs_per_line)
        self.assertEqual(len(refs_per_line["10k"]), 2)
        self.assertIn("R1", refs_per_line["10k"])
        self.assertIn("R2", refs_per_line["10k"])

    def test_unique_parts_count_correct(self):
        """7 components with 5 unique value+footprint combos."""
        result = self.gen.generate(self._make_components())
        self.assertEqual(result.unique_parts, 5)

    def test_total_parts_count_correct(self):
        """Total parts should equal number of component instances."""
        result = self.gen.generate(self._make_components())
        self.assertEqual(result.total_parts, 7)

    def test_dnp_components_excluded_from_cost(self):
        """DNP components should not contribute to estimated cost."""
        comps_with_dnp = self._make_components()
        comps_without_dnp = [c for c in comps_with_dnp if not c.dnp]
        result_with    = self.gen.generate(comps_with_dnp)
        result_without = self.gen.generate(comps_without_dnp)
        self.assertAlmostEqual(result_with.estimated_cost, result_without.estimated_cost, places=4)

    def test_dnp_count_correct(self):
        """DNP count should equal number of DNP component instances."""
        result = self.gen.generate(self._make_components())
        self.assertEqual(result.dnp_count, 1)

    def test_quantity_price_break_applied(self):
        """Ordering 100 boards should give lower unit price than 1 board."""
        comps = [Component("R1", "10k", "Resistor_SMD:R_0402")]
        result_1   = self.gen.generate(comps, board_quantity=1)
        result_100 = self.gen.generate(comps, board_quantity=100)
        # Unit price at qty=100 should be lower
        line_1   = result_1.lines[0]
        line_100 = result_100.lines[0]
        self.assertLessEqual(line_100.unit_cost, line_1.unit_cost)

    def test_total_cost_positive(self):
        """Estimated cost should be positive for non-DNP components."""
        result = self.gen.generate(self._make_components())
        self.assertGreater(result.estimated_cost, 0.0)

    def test_csv_export_has_header(self):
        """CSV export should have a header row."""
        result = self.gen.generate(self._make_components())
        csv_str = self.gen.to_csv(result)
        self.assertIn("Comment", csv_str)
        self.assertIn("Designator", csv_str)
        self.assertIn("LCSC Part #", csv_str)

    def test_csv_export_contains_all_values(self):
        """CSV should contain all unique component values."""
        result = self.gen.generate(self._make_components())
        csv_str = self.gen.to_csv(result)
        self.assertIn("10k", csv_str)
        self.assertIn("100nF", csv_str)
        self.assertIn("STM32F411", csv_str)

    def test_json_export_valid_json(self):
        """JSON export should produce valid JSON."""
        result = self.gen.generate(self._make_components())
        json_str = self.gen.to_json(result)
        data = json.loads(json_str)
        self.assertIn("summary", data)
        self.assertIn("lines", data)
        self.assertEqual(data["summary"]["total_parts"], 7)

    def test_total_cost_line_sum_matches_result(self):
        """Sum of line total_costs should equal result.estimated_cost."""
        result = self.gen.generate(self._make_components())
        line_total = sum(l.total_cost for l in result.lines if not l.dnp)
        self.assertAlmostEqual(line_total, result.estimated_cost, places=4)


# ─── Gerber Tests ─────────────────────────────────────────────────────────────

_VALID_GERBER = """%FSLAX46Y46*%
%MOMM*%
%ADD10C,0.100000*%
%ADD11R,0.200000X0.200000*%
G04 Top copper layer*
X0Y0D02*
X1000000Y0D01*
X1000000Y1000000D01*
X0Y1000000D01*
X0Y0D01*
X500000Y500000D03*
M02*
"""

_INVALID_GERBER_NO_FORMAT = """%MOMM*%
%ADD10C,0.100000*%
X0Y0D02*
M02*
"""

_INVALID_GERBER_BAD_APERTURE = """%FSLAX46Y46*%
%MOMM*%
%ADD5C,0.100000*%
X0Y0D03*
M02*
"""


class TestGerberParser(unittest.TestCase):

    def setUp(self):
        self.parser = GerberParser()

    def test_valid_gerber_parses_correctly(self):
        """Valid Gerber should parse with no errors."""
        stats = self.parser.parse(_VALID_GERBER, layer=GerberLayer.COPPER_TOP)
        self.assertTrue(stats.is_valid)
        self.assertEqual(len(stats.errors), 0)

    def test_aperture_count_correct(self):
        """Valid Gerber has 2 aperture definitions."""
        stats = self.parser.parse(_VALID_GERBER)
        self.assertEqual(stats.aperture_count, 2)

    def test_flash_count_correct(self):
        """Valid Gerber has 1 flash command (D03)."""
        stats = self.parser.parse(_VALID_GERBER)
        self.assertEqual(stats.flash_count, 1)

    def test_draw_count_correct(self):
        """Valid Gerber has 4 draw commands (D01)."""
        stats = self.parser.parse(_VALID_GERBER)
        self.assertEqual(stats.draw_command_count, 4)

    def test_unit_detected_as_mm(self):
        """Valid Gerber with %MOMM% should report MM units."""
        stats = self.parser.parse(_VALID_GERBER)
        self.assertEqual(stats.unit, "MM")

    def test_missing_format_spec_is_error(self):
        """Gerber without %FS should report format spec error."""
        stats = self.parser.parse(_INVALID_GERBER_NO_FORMAT)
        self.assertFalse(stats.is_valid)
        self.assertTrue(any("format" in e.lower() for e in stats.errors))

    def test_invalid_aperture_code_is_error(self):
        """Aperture D5 (< D10) should be reported as error."""
        stats = self.parser.parse(_INVALID_GERBER_BAD_APERTURE)
        self.assertFalse(stats.is_valid)
        self.assertTrue(any("aperture" in e.lower() for e in stats.errors))

    def test_has_format_spec_true_for_valid(self):
        """has_format_spec should be True for valid Gerber."""
        stats = self.parser.parse(_VALID_GERBER)
        self.assertTrue(stats.has_format_spec)

    def test_has_units_true_for_valid(self):
        """has_units should be True for valid Gerber."""
        stats = self.parser.parse(_VALID_GERBER)
        self.assertTrue(stats.has_units)


class TestManufacturingValidator(unittest.TestCase):

    def setUp(self):
        self.validator = ManufacturingValidator(layer_count=2)

    def _make_valid_package(self):
        return ManufacturingPackage(
            layers={
                GerberLayer.COPPER_TOP:    _VALID_GERBER,
                GerberLayer.COPPER_BOTTOM: _VALID_GERBER,
                GerberLayer.MASK_TOP:      _VALID_GERBER,
                GerberLayer.MASK_BOTTOM:   _VALID_GERBER,
                GerberLayer.EDGE_CUTS:     _VALID_GERBER,
                GerberLayer.DRILL:         _VALID_GERBER,
            }
        )

    def test_complete_valid_package_passes(self):
        """Package with all required layers and valid Gerbers should pass."""
        result = self.validator.validate(self._make_valid_package())
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_missing_layer_fails(self):
        """Package missing EDGE_CUTS should fail."""
        package = self._make_valid_package()
        del package.layers[GerberLayer.EDGE_CUTS]
        result = self.validator.validate(package)
        self.assertFalse(result.is_valid)
        self.assertIn(GerberLayer.EDGE_CUTS, result.missing_layers)

    def test_missing_drill_fails(self):
        """Package missing Drill file should fail."""
        package = self._make_valid_package()
        del package.layers[GerberLayer.DRILL]
        result = self.validator.validate(package)
        self.assertFalse(result.is_valid)
        self.assertIn(GerberLayer.DRILL, result.missing_layers)

    def test_invalid_gerber_in_layer_fails(self):
        """Package with invalid Gerber in one layer should fail."""
        package = self._make_valid_package()
        package.layers[GerberLayer.COPPER_TOP] = _INVALID_GERBER_NO_FORMAT
        result = self.validator.validate(package)
        self.assertFalse(result.is_valid)

    def test_present_layers_listed_correctly(self):
        """present_layers should list all layers that were provided."""
        package = self._make_valid_package()
        result = self.validator.validate(package)
        self.assertEqual(len(result.present_layers), 6)

    def test_layer_stats_populated(self):
        """layer_stats should contain stats for each present layer."""
        package = self._make_valid_package()
        result = self.validator.validate(package)
        self.assertIn(GerberLayer.COPPER_TOP.value, result.layer_stats)

    def test_inconsistent_units_fails(self):
        """Package with MM and IN layers should fail unit consistency check."""
        _INCH_GERBER = """%FSLAX46Y46*%
%MOIN*%
%ADD10C,0.004000*%
X0Y0D02*
M02*
"""
        package = self._make_valid_package()
        package.layers[GerberLayer.COPPER_BOTTOM] = _INCH_GERBER
        result = self.validator.validate(package)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("unit" in e.lower() for e in result.errors))


if __name__ == '__main__':
    unittest.main(verbosity=2)
