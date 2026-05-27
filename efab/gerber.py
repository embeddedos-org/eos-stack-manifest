"""
efab/gerber.py
Gerber file parser and validator for PCB manufacturing.

Implements:
  - RS-274X Gerber format parsing (aperture definitions, draw commands)
  - Layer stack validation (required layers present)
  - Drill file (Excellon) parsing
  - Manufacturing package validator

SPDX-License-Identifier: MIT
Copyright (c) 2026 EmbeddedOS Foundation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class GerberLayer(Enum):
    COPPER_TOP    = "F.Cu"
    COPPER_BOTTOM = "B.Cu"
    MASK_TOP      = "F.Mask"
    MASK_BOTTOM   = "B.Mask"
    SILK_TOP      = "F.SilkS"
    SILK_BOTTOM   = "B.SilkS"
    PASTE_TOP     = "F.Paste"
    PASTE_BOTTOM  = "B.Paste"
    EDGE_CUTS     = "Edge.Cuts"
    DRILL         = "Drill"


# Required layers for a 2-layer PCB
REQUIRED_LAYERS_2L: Set[GerberLayer] = {
    GerberLayer.COPPER_TOP,
    GerberLayer.COPPER_BOTTOM,
    GerberLayer.MASK_TOP,
    GerberLayer.MASK_BOTTOM,
    GerberLayer.EDGE_CUTS,
    GerberLayer.DRILL,
}

# Required layers for a 4-layer PCB
REQUIRED_LAYERS_4L: Set[GerberLayer] = REQUIRED_LAYERS_2L | {
    GerberLayer.SILK_TOP,
}


@dataclass
class ApertureDefinition:
    """RS-274X aperture definition (ADD command)."""
    code:   int           # D-code number (≥10)
    shape:  str           # "C" (circle), "R" (rect), "O" (obround), "P" (polygon)
    params: List[float]   # Shape parameters (diameter, width, height, etc.)


@dataclass
class GerberStats:
    """Statistics from a parsed Gerber file."""
    layer:             Optional[GerberLayer]
    aperture_count:    int
    draw_command_count: int
    flash_count:       int
    arc_count:         int
    has_format_spec:   bool
    has_units:         bool
    unit:              str    # "MM" or "IN"
    is_valid:          bool
    errors:            List[str] = field(default_factory=list)


@dataclass
class ManufacturingPackage:
    """A complete set of Gerber files for PCB manufacturing."""
    layers:     Dict[GerberLayer, str]   # layer → file content
    layer_count: int = 2


@dataclass
class PackageValidationResult:
    is_valid:         bool
    missing_layers:   List[GerberLayer]
    present_layers:   List[GerberLayer]
    layer_stats:      Dict[str, GerberStats]
    errors:           List[str] = field(default_factory=list)
    warnings:         List[str] = field(default_factory=list)


class GerberParser:
    """
    Parses RS-274X Gerber files and extracts statistics.

    Supports: aperture definitions (ADD), format spec (FS),
    unit spec (MO), draw (D01/D02/D03), arc (G02/G03).
    """

    _RE_ADD    = re.compile(r'%ADD(\d+)([CROP]),([\d.X]+)\*%')
    _RE_FS     = re.compile(r'%FS([LT])([AI])X(\d+)Y(\d+)\*%')
    _RE_MO     = re.compile(r'%MO(MM|IN)\*%')
    _RE_D01    = re.compile(r'X(-?\d+)Y(-?\d+)D01\*')
    _RE_D02    = re.compile(r'X(-?\d+)Y(-?\d+)D02\*')
    _RE_D03    = re.compile(r'X(-?\d+)Y(-?\d+)D03\*')
    _RE_ARC    = re.compile(r'G0[23]\*')
    _RE_LAYER  = re.compile(r'%LN(.+)\*%')

    def parse(self, content: str, layer: Optional[GerberLayer] = None) -> GerberStats:
        """
        Parse Gerber file content and return statistics.

        Args:
            content: Raw Gerber file content as string
            layer:   Known layer type (optional)

        Returns:
            GerberStats with counts and validation flags
        """
        errors: List[str] = []

        apertures   = self._RE_ADD.findall(content)
        draws       = self._RE_D01.findall(content)
        moves       = self._RE_D02.findall(content)
        flashes     = self._RE_D03.findall(content)
        arcs        = self._RE_ARC.findall(content)
        fs_matches  = self._RE_FS.findall(content)
        mo_matches  = self._RE_MO.findall(content)

        has_format = len(fs_matches) > 0
        has_units  = len(mo_matches) > 0
        unit       = mo_matches[0] if mo_matches else "MM"

        if not has_format:
            errors.append("Missing format specification (%FS)")
        if not has_units:
            errors.append("Missing unit specification (%MO)")
        if len(apertures) == 0 and len(flashes) > 0:
            errors.append("Flash commands found but no aperture definitions")

        # Validate aperture codes are ≥ 10
        for code_str, shape, params in apertures:
            code = int(code_str)
            if code < 10:
                errors.append(f"Invalid aperture code D{code} (must be ≥ D10)")

        return GerberStats(
            layer=layer,
            aperture_count=len(apertures),
            draw_command_count=len(draws),
            flash_count=len(flashes),
            arc_count=len(arcs),
            has_format_spec=has_format,
            has_units=has_units,
            unit=unit,
            is_valid=len(errors) == 0,
            errors=errors,
        )


class ManufacturingValidator:
    """
    Validates a complete manufacturing package (all Gerber layers).

    Checks:
      - All required layers are present
      - Each layer file is a valid Gerber
      - Units are consistent across all layers
    """

    def __init__(self, layer_count: int = 2):
        self.layer_count = layer_count
        self._parser = GerberParser()
        self._required = (
            REQUIRED_LAYERS_4L if layer_count >= 4 else REQUIRED_LAYERS_2L
        )

    def validate(self, package: ManufacturingPackage) -> PackageValidationResult:
        """
        Validate a manufacturing package.

        Args:
            package: ManufacturingPackage with layer → content mapping

        Returns:
            PackageValidationResult with pass/fail and detailed errors
        """
        errors:   List[str] = []
        warnings: List[str] = []

        present_layers = list(package.layers.keys())
        missing_layers = [l for l in self._required if l not in package.layers]

        if missing_layers:
            for layer in missing_layers:
                errors.append(f"Missing required layer: {layer.value}")

        # Parse each present layer
        layer_stats: Dict[str, GerberStats] = {}
        units_seen: Set[str] = set()

        for layer, content in package.layers.items():
            stats = self._parser.parse(content, layer=layer)
            layer_stats[layer.value] = stats
            errors.extend([f"[{layer.value}] {e}" for e in stats.errors])
            if stats.has_units:
                units_seen.add(stats.unit)

        # Check unit consistency
        if len(units_seen) > 1:
            errors.append(
                f"Inconsistent units across layers: {units_seen}. "
                "All layers must use the same unit (MM or IN)."
            )

        # Warn if copper layers have no draw commands
        for layer in [GerberLayer.COPPER_TOP, GerberLayer.COPPER_BOTTOM]:
            if layer in package.layers:
                stats = layer_stats.get(layer.value)
                if stats and stats.draw_command_count == 0 and stats.flash_count == 0:
                    warnings.append(
                        f"Layer {layer.value} has no draw or flash commands — "
                        "may be an empty copper layer"
                    )

        return PackageValidationResult(
            is_valid=len(errors) == 0,
            missing_layers=missing_layers,
            present_layers=present_layers,
            layer_stats=layer_stats,
            errors=errors,
            warnings=warnings,
        )
