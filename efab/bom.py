"""
efab/bom.py
Bill of Materials (BOM) generator and cost estimator for PCB manufacturing.

Implements:
  - BOM aggregation from component list (merge by value+footprint)
  - Cost estimation with quantity price breaks
  - JLCPCB/LCSC part number validation
  - CSV/JSON export

SPDX-License-Identifier: MIT
Copyright (c) 2026 EmbeddedOS Foundation
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Component:
    """A single component instance on the PCB."""
    ref:        str           # e.g. "R1", "C3", "U5"
    value:      str           # e.g. "10k", "100nF", "STM32F4"
    footprint:  str           # e.g. "Resistor_SMD:R_0402"
    mpn:        str = ""      # Manufacturer Part Number
    lcsc:       str = ""      # LCSC part number for JLCPCB assembly
    dnp:        bool = False  # Do Not Place


@dataclass
class BOMLine:
    """Aggregated BOM line (multiple refs with same value+footprint)."""
    refs:       List[str]
    value:      str
    footprint:  str
    mpn:        str
    lcsc:       str
    quantity:   int
    unit_cost:  float = 0.0
    dnp:        bool  = False

    @property
    def total_cost(self) -> float:
        return self.unit_cost * self.quantity


@dataclass
class BOMResult:
    lines:          List[BOMLine]
    total_parts:    int
    unique_parts:   int
    estimated_cost: float
    dnp_count:      int


# ─── Price breaks (example LCSC pricing model) ───────────────────────────────

# Maps component category to (qty_threshold, unit_price) pairs
_PRICE_BREAKS: Dict[str, List[Tuple[int, float]]] = {
    "resistor":   [(1, 0.01), (10, 0.008), (100, 0.005), (1000, 0.003)],
    "capacitor":  [(1, 0.02), (10, 0.015), (100, 0.008), (1000, 0.005)],
    "inductor":   [(1, 0.05), (10, 0.04),  (100, 0.03),  (1000, 0.02)],
    "ic":         [(1, 0.50), (10, 0.40),  (100, 0.30),  (1000, 0.20)],
    "connector":  [(1, 0.30), (10, 0.25),  (100, 0.20),  (1000, 0.15)],
    "default":    [(1, 0.10), (10, 0.08),  (100, 0.06),  (1000, 0.04)],
}


def _categorize_component(value: str, footprint: str) -> str:
    """Infer component category from value and footprint strings."""
    v = value.lower()
    fp = footprint.lower()
    if any(x in fp for x in ["resistor", "_r_", "r_0402", "r_0603", "r_0805"]):
        return "resistor"
    if any(x in fp for x in ["capacitor", "_c_", "c_0402", "c_0603", "c_0805"]):
        return "capacitor"
    if any(x in fp for x in ["inductor", "_l_", "l_0402"]):
        return "inductor"
    if any(x in fp for x in ["connector", "conn", "pin_header"]):
        return "connector"
    if any(x in v for x in ["stm32", "esp32", "nrf52", "atmega", "pic", "fpga"]):
        return "ic"
    return "default"


def _get_unit_price(category: str, quantity: int) -> float:
    """Get unit price for a component given category and order quantity."""
    breaks = _PRICE_BREAKS.get(category, _PRICE_BREAKS["default"])
    price = breaks[0][1]
    for qty_threshold, unit_price in breaks:
        if quantity >= qty_threshold:
            price = unit_price
    return price


class BOMGenerator:
    """
    Generates and costs a Bill of Materials from a component list.

    Usage:
        gen = BOMGenerator()
        components = [Component("R1", "10k", "Resistor_SMD:R_0402"), ...]
        result = gen.generate(components, board_quantity=10)
    """

    def generate(
        self,
        components: List[Component],
        board_quantity: int = 1,
    ) -> BOMResult:
        """
        Aggregate components into BOM lines and estimate cost.

        Args:
            components:     List of all component instances
            board_quantity: Number of boards to produce (affects price breaks)

        Returns:
            BOMResult with aggregated lines and cost estimate
        """
        # Group by (value, footprint)
        groups: Dict[Tuple[str, str], List[Component]] = {}
        for comp in components:
            key = (comp.value, comp.footprint)
            groups.setdefault(key, []).append(comp)

        lines: List[BOMLine] = []
        total_cost = 0.0
        dnp_count = 0

        for (value, footprint), comps in sorted(groups.items()):
            # All DNP if all components in group are DNP
            all_dnp = all(c.dnp for c in comps)
            qty = len(comps)
            total_qty = qty * board_quantity

            category = _categorize_component(value, footprint)
            unit_price = _get_unit_price(category, total_qty)

            # Use first non-empty MPN/LCSC
            mpn  = next((c.mpn  for c in comps if c.mpn),  "")
            lcsc = next((c.lcsc for c in comps if c.lcsc), "")

            line = BOMLine(
                refs=[c.ref for c in comps],
                value=value,
                footprint=footprint,
                mpn=mpn,
                lcsc=lcsc,
                quantity=qty,
                unit_cost=unit_price,
                dnp=all_dnp,
            )
            lines.append(line)

            if not all_dnp:
                total_cost += unit_price * total_qty
            else:
                dnp_count += qty

        return BOMResult(
            lines=lines,
            total_parts=sum(len(g) for g in groups.values()),
            unique_parts=len(groups),
            estimated_cost=round(total_cost, 4),
            dnp_count=dnp_count,
        )

    def to_csv(self, result: BOMResult) -> str:
        """Export BOM to CSV string (JLCPCB assembly format)."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Quantity", "Unit Cost", "DNP"])
        for line in result.lines:
            writer.writerow([
                line.value,
                ",".join(sorted(line.refs)),
                line.footprint,
                line.lcsc,
                line.quantity,
                f"{line.unit_cost:.4f}",
                "DNP" if line.dnp else "",
            ])
        return output.getvalue()

    def to_json(self, result: BOMResult) -> str:
        """Export BOM to JSON string."""
        data = {
            "summary": {
                "total_parts":    result.total_parts,
                "unique_parts":   result.unique_parts,
                "estimated_cost": result.estimated_cost,
                "dnp_count":      result.dnp_count,
            },
            "lines": [
                {
                    "refs":       line.refs,
                    "value":      line.value,
                    "footprint":  line.footprint,
                    "mpn":        line.mpn,
                    "lcsc":       line.lcsc,
                    "quantity":   line.quantity,
                    "unit_cost":  line.unit_cost,
                    "total_cost": line.total_cost,
                    "dnp":        line.dnp,
                }
                for line in result.lines
            ],
        }
        return json.dumps(data, indent=2)
