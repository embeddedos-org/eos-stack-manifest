"""
tests/test_drc.py
Real unit tests for eFab DRC engine.
All assertions call real DRC functions with real PCB data.
Run: python3 -m pytest tests/ -v
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from efab.drc import (
    DRCEngine, DRCRules, PCBDesign, TraceSegment, Via, Pad, Severity
)


class TestDRCTraceWidth(unittest.TestCase):

    def setUp(self):
        self.engine = DRCEngine(rules=DRCRules())

    def _design_with_trace(self, net, width_mm, layer="F.Cu"):
        design = PCBDesign(name="test")
        design.traces.append(TraceSegment(
            net=net, width_mm=width_mm, length_mm=10.0,
            layer=layer, start=(0, 0), end=(10, 0)
        ))
        return design

    def test_trace_above_minimum_passes(self):
        """Trace at 0.2mm (above 0.127mm minimum) should pass."""
        result = self.engine.run(self._design_with_trace("SIG", 0.2))
        self.assertTrue(result.passed)
        self.assertEqual(result.error_count, 0)

    def test_trace_below_minimum_fails(self):
        """Trace at 0.05mm (below 0.127mm minimum) should fail."""
        result = self.engine.run(self._design_with_trace("SIG", 0.05))
        self.assertFalse(result.passed)
        self.assertEqual(result.error_count, 1)
        self.assertEqual(result.violations[0].rule, "TRACE_WIDTH")

    def test_trace_at_exact_minimum_passes(self):
        """Trace exactly at minimum (0.127mm) should pass."""
        result = self.engine.run(self._design_with_trace("SIG", 0.127))
        self.assertTrue(result.passed)

    def test_power_net_requires_wider_trace(self):
        """GND trace at 0.2mm (below 0.5mm power minimum) should fail."""
        result = self.engine.run(self._design_with_trace("GND", 0.2))
        self.assertFalse(result.passed)
        self.assertIn("TRACE_WIDTH", [v.rule for v in result.violations])

    def test_power_net_wide_trace_passes(self):
        """VCC trace at 0.6mm (above 0.5mm power minimum) should pass."""
        result = self.engine.run(self._design_with_trace("VCC", 0.6))
        self.assertTrue(result.passed)

    def test_violation_contains_net_name(self):
        """Violation message should contain the net name."""
        result = self.engine.run(self._design_with_trace("MOSI", 0.05))
        self.assertFalse(result.passed)
        self.assertIn("MOSI", result.violations[0].message)

    def test_violation_severity_is_error(self):
        """Trace width violation should be ERROR severity."""
        result = self.engine.run(self._design_with_trace("SIG", 0.05))
        self.assertEqual(result.violations[0].severity, Severity.ERROR)


class TestDRCViaDimensions(unittest.TestCase):

    def setUp(self):
        self.engine = DRCEngine(rules=DRCRules())

    def _design_with_via(self, drill_mm, pad_mm):
        design = PCBDesign(name="test")
        design.vias.append(Via(
            net="GND", drill_mm=drill_mm, pad_mm=pad_mm, location=(5.0, 5.0)
        ))
        return design

    def test_valid_via_passes(self):
        """Via with drill=0.3mm, pad=0.6mm should pass."""
        result = self.engine.run(self._design_with_via(0.3, 0.6))
        self.assertTrue(result.passed)

    def test_drill_too_small_fails(self):
        """Via with drill=0.1mm (below 0.2mm minimum) should fail."""
        result = self.engine.run(self._design_with_via(0.1, 0.6))
        self.assertFalse(result.passed)
        rules = [v.rule for v in result.violations]
        self.assertIn("VIA_DRILL", rules)

    def test_pad_too_small_fails(self):
        """Via with pad=0.3mm (below 0.4mm minimum) should fail."""
        result = self.engine.run(self._design_with_via(0.3, 0.3))
        self.assertFalse(result.passed)
        rules = [v.rule for v in result.violations]
        self.assertIn("VIA_PAD", rules)

    def test_annular_ring_too_small_fails(self):
        """Via with drill=0.35mm, pad=0.4mm → annular=0.025mm < 0.05mm min."""
        result = self.engine.run(self._design_with_via(0.35, 0.4))
        self.assertFalse(result.passed)
        rules = [v.rule for v in result.violations]
        self.assertIn("VIA_ANNULAR_RING", rules)

    def test_multiple_via_errors_reported(self):
        """Via with both drill and pad too small should report multiple errors."""
        result = self.engine.run(self._design_with_via(0.1, 0.2))
        self.assertGreaterEqual(result.error_count, 2)


class TestDRCPadClearance(unittest.TestCase):

    def setUp(self):
        self.engine = DRCEngine(rules=DRCRules())

    def _design_with_pads(self, x1, x2, net1="NET1", net2="NET2"):
        design = PCBDesign(name="test")
        design.pads.append(Pad(
            ref="U1", net=net1, pad_num="1",
            location=(x1, 0.0), size_mm=(0.5, 0.5)
        ))
        design.pads.append(Pad(
            ref="U1", net=net2, pad_num="2",
            location=(x2, 0.0), size_mm=(0.5, 0.5)
        ))
        return design

    def test_pads_with_sufficient_clearance_pass(self):
        """Pads 2mm apart (edge-to-edge ~1.5mm) should pass."""
        result = self.engine.run(self._design_with_pads(0.0, 2.0))
        self.assertTrue(result.passed)

    def test_pads_too_close_fail(self):
        """Pads 0.5mm apart (edge-to-edge = 0mm) should fail."""
        result = self.engine.run(self._design_with_pads(0.0, 0.5))
        self.assertFalse(result.passed)
        self.assertIn("PAD_CLEARANCE", [v.rule for v in result.violations])

    def test_same_net_pads_no_clearance_required(self):
        """Pads on the same net should not trigger clearance violation."""
        result = self.engine.run(self._design_with_pads(0.0, 0.3, "GND", "GND"))
        # Same net — no clearance check
        pad_violations = [v for v in result.violations if v.rule == "PAD_CLEARANCE"]
        self.assertEqual(len(pad_violations), 0)


class TestDRCResult(unittest.TestCase):

    def test_empty_design_passes(self):
        """Empty design with no traces/vias/pads should pass."""
        engine = DRCEngine()
        result = engine.run(PCBDesign(name="empty"))
        self.assertTrue(result.passed)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 0)

    def test_error_count_correct(self):
        """error_count property should count only ERROR severity violations."""
        engine = DRCEngine()
        design = PCBDesign(name="test")
        # Add two bad traces
        for i in range(2):
            design.traces.append(TraceSegment(
                net=f"SIG{i}", width_mm=0.05, length_mm=5.0,
                layer="F.Cu", start=(i*10, 0), end=(i*10+5, 0)
            ))
        result = engine.run(design)
        self.assertEqual(result.error_count, 2)

    def test_passed_false_when_errors_exist(self):
        """passed property should be False when any ERROR violations exist."""
        engine = DRCEngine()
        design = PCBDesign(name="test")
        design.traces.append(TraceSegment(
            net="SIG", width_mm=0.01, length_mm=5.0,
            layer="F.Cu", start=(0, 0), end=(5, 0)
        ))
        result = engine.run(design)
        self.assertFalse(result.passed)


if __name__ == '__main__':
    unittest.main(verbosity=2)
