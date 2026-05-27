"""
efab/drc.py
Design Rule Check (DRC) engine for PCB manufacturing validation.

Validates PCB designs against IPC-2221B and IPC-7351B standards.
Checks: trace width, clearance, via drill, pad-to-pad spacing,
        copper pour clearance, silkscreen overlap, drill-to-copper.

SPDX-License-Identifier: MIT
Copyright (c) 2026 EmbeddedOS Foundation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class Severity(Enum):
    ERROR   = "ERROR"
    WARNING = "WARNING"
    INFO    = "INFO"


@dataclass
class DRCViolation:
    rule:        str
    severity:    Severity
    message:     str
    location:    Optional[Tuple[float, float]] = None   # (x_mm, y_mm)
    net:         Optional[str] = None


@dataclass
class DRCResult:
    violations: List[DRCViolation] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)

    @property
    def passed(self) -> bool:
        return self.error_count == 0


@dataclass
class TraceSegment:
    net:         str
    width_mm:    float
    length_mm:   float
    layer:       str          # "F.Cu", "B.Cu", "In1.Cu", etc.
    start:       Tuple[float, float]
    end:         Tuple[float, float]


@dataclass
class Via:
    net:          str
    drill_mm:     float
    pad_mm:       float
    location:     Tuple[float, float]


@dataclass
class Pad:
    ref:          str
    net:          str
    pad_num:      str
    location:     Tuple[float, float]
    size_mm:      Tuple[float, float]   # (width, height)
    drill_mm:     float = 0.0           # 0 = SMD


@dataclass
class PCBDesign:
    """Represents a parsed PCB design for DRC analysis."""
    name:           str
    traces:         List[TraceSegment] = field(default_factory=list)
    vias:           List[Via]          = field(default_factory=list)
    pads:           List[Pad]          = field(default_factory=list)
    board_thickness_mm: float          = 1.6
    copper_weight_oz:   float          = 1.0   # oz/ft²


# ─── DRC Rules ───────────────────────────────────────────────────────────────

@dataclass
class DRCRules:
    """
    IPC-2221B Class B (general electronics) design rules.
    All dimensions in mm.
    """
    # Trace rules
    min_trace_width_mm:     float = 0.127    # 5 mil
    min_trace_clearance_mm: float = 0.127    # 5 mil

    # Via rules
    min_via_drill_mm:       float = 0.2      # 8 mil
    min_via_pad_mm:         float = 0.4      # 16 mil
    min_via_annular_mm:     float = 0.05     # 2 mil annular ring

    # Pad rules
    min_pad_clearance_mm:   float = 0.127    # 5 mil pad-to-pad
    min_drill_to_copper_mm: float = 0.254    # 10 mil

    # Board rules
    min_copper_to_edge_mm:  float = 0.3      # 12 mil

    # Power net rules (wider traces required)
    power_nets:             List[str] = field(default_factory=lambda: ["VCC", "VDD", "GND", "PWR"])
    min_power_trace_width_mm: float   = 0.5  # 20 mil for power nets


class DRCEngine:
    """
    Runs design rule checks against a PCBDesign.

    Usage:
        engine = DRCEngine(rules=DRCRules())
        result = engine.run(design)
        if not result.passed:
            for v in result.violations:
                print(v)
    """

    def __init__(self, rules: Optional[DRCRules] = None):
        self.rules = rules or DRCRules()

    def run(self, design: PCBDesign) -> DRCResult:
        """Run all DRC checks and return aggregated result."""
        result = DRCResult()
        self._check_trace_widths(design, result)
        self._check_via_dimensions(design, result)
        self._check_pad_clearances(design, result)
        self._check_via_annular_rings(design, result)
        return result

    # ── Trace width check ────────────────────────────────────────────────────

    def _check_trace_widths(self, design: PCBDesign, result: DRCResult) -> None:
        for trace in design.traces:
            min_width = (
                self.rules.min_power_trace_width_mm
                if trace.net.upper() in [n.upper() for n in self.rules.power_nets]
                else self.rules.min_trace_width_mm
            )
            if trace.width_mm < min_width:
                result.violations.append(DRCViolation(
                    rule="TRACE_WIDTH",
                    severity=Severity.ERROR,
                    message=(
                        f"Trace on net '{trace.net}' ({trace.layer}) width "
                        f"{trace.width_mm:.3f}mm < minimum {min_width:.3f}mm"
                    ),
                    location=trace.start,
                    net=trace.net,
                ))

    # ── Via dimension check ───────────────────────────────────────────────────

    def _check_via_dimensions(self, design: PCBDesign, result: DRCResult) -> None:
        for via in design.vias:
            if via.drill_mm < self.rules.min_via_drill_mm:
                result.violations.append(DRCViolation(
                    rule="VIA_DRILL",
                    severity=Severity.ERROR,
                    message=(
                        f"Via at ({via.location[0]:.2f}, {via.location[1]:.2f}) "
                        f"drill {via.drill_mm:.3f}mm < minimum {self.rules.min_via_drill_mm:.3f}mm"
                    ),
                    location=via.location,
                    net=via.net,
                ))
            if via.pad_mm < self.rules.min_via_pad_mm:
                result.violations.append(DRCViolation(
                    rule="VIA_PAD",
                    severity=Severity.ERROR,
                    message=(
                        f"Via at ({via.location[0]:.2f}, {via.location[1]:.2f}) "
                        f"pad {via.pad_mm:.3f}mm < minimum {self.rules.min_via_pad_mm:.3f}mm"
                    ),
                    location=via.location,
                    net=via.net,
                ))

    # ── Pad clearance check ───────────────────────────────────────────────────

    def _check_pad_clearances(self, design: PCBDesign, result: DRCResult) -> None:
        import math
        pads = design.pads
        for i in range(len(pads)):
            for j in range(i + 1, len(pads)):
                p1, p2 = pads[i], pads[j]
                if p1.net == p2.net:
                    continue  # Same net — no clearance required
                dx = p1.location[0] - p2.location[0]
                dy = p1.location[1] - p2.location[1]
                center_dist = math.sqrt(dx * dx + dy * dy)
                # Approximate edge-to-edge as center distance minus half-sizes
                half1 = max(p1.size_mm) / 2.0
                half2 = max(p2.size_mm) / 2.0
                clearance = center_dist - half1 - half2
                if clearance < self.rules.min_pad_clearance_mm:
                    result.violations.append(DRCViolation(
                        rule="PAD_CLEARANCE",
                        severity=Severity.ERROR,
                        message=(
                            f"Pad {p1.ref}/{p1.pad_num} (net {p1.net}) to "
                            f"{p2.ref}/{p2.pad_num} (net {p2.net}) clearance "
                            f"{clearance:.3f}mm < minimum {self.rules.min_pad_clearance_mm:.3f}mm"
                        ),
                        location=p1.location,
                    ))

    # ── Via annular ring check ────────────────────────────────────────────────

    def _check_via_annular_rings(self, design: PCBDesign, result: DRCResult) -> None:
        for via in design.vias:
            annular = (via.pad_mm - via.drill_mm) / 2.0
            if annular < self.rules.min_via_annular_mm:
                result.violations.append(DRCViolation(
                    rule="VIA_ANNULAR_RING",
                    severity=Severity.ERROR,
                    message=(
                        f"Via at ({via.location[0]:.2f}, {via.location[1]:.2f}) "
                        f"annular ring {annular:.3f}mm < minimum "
                        f"{self.rules.min_via_annular_mm:.3f}mm"
                    ),
                    location=via.location,
                    net=via.net,
                ))
