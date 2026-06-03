#!/usr/bin/env python3
"""
EmbeddedOS eBuild — CAD Product Simulation Runner
==================================================
Discovers and executes all power_budget_sim.py files across every
eCAD-Hardware-Products division, then prints a build-time summary table.

Usage:
    # Run against local checkout of eCAD-Hardware-Products:
    python3 scripts/run-ecad-simulations.py --ecad-root ../eCAD-Hardware-Products

    # Run with inline fallback simulations (no checkout needed):
    python3 scripts/run-ecad-simulations.py

    # Run a specific division only:
    python3 scripts/run-ecad-simulations.py --division eAerospace_CAD_Design

    # Output GitHub Step Summary markdown:
    python3 scripts/run-ecad-simulations.py --github-summary

Exit codes:
    0  All simulations passed
    1  One or more simulations failed
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

# ── ANSI colours (disabled on Windows / non-TTY) ──────────────────────────
_USE_COLOUR = sys.stdout.isatty() and sys.platform != "win32"
GREEN  = "\033[32m" if _USE_COLOUR else ""
RED    = "\033[31m" if _USE_COLOUR else ""
YELLOW = "\033[33m" if _USE_COLOUR else ""
BOLD   = "\033[1m"  if _USE_COLOUR else ""
RESET  = "\033[0m"  if _USE_COLOUR else ""

# ── Known divisions and their product sub-categories ──────────────────────
DIVISIONS: dict[str, list[str]] = {
    "eAerospace_CAD_Design":     ["avionics", "aircraft_components", "uav_drone_systems", "space_systems"],
    "eMedical_CAD_Design":       ["medical_devices", "surgical_robotics", "diagnostic_equipment", "implantable_devices"],
    "eIndustrial_CAD_Design":    ["industrial_automation", "process_control", "industrial_iot"],
    "eDefense_CAD_Design":       ["military_electronics", "surveillance_systems", "communication_systems"],
    "eRobotics_CAD_Design":      ["autonomous_systems", "industrial_robots", "robot_components"],
    "eEnergy_CAD_Design":        ["battery_management", "renewable_energy", "power_electronics"],
    "eTransport_CAD_Design":     ["automotive_electronics", "rail_systems", "maritime_systems"],
    "eElectronics_CAD_Design":   ["electronic_components", "semiconductor_products", "emerging_tech"],
    "eSmartCity_CAD_Design":     ["urban_infrastructure", "utilities", "telecom"],
    "eCybersecurity_CAD_Design": ["security_appliances", "physical_security"],
    "eConsumer_CAD_Design":      ["smart_home", "personal_devices", "smart_devices"],
    "eMining_CAD_Design":        ["mining_equipment", "industrial_safety", "construction_robots"],
    # AeroSwift products (merged into eos-aero)
    "AeroSwift":                 ["aeroswift_personal", "aeroswift_transit", "shared_platform"],
    # ePAM existing products
    "ePAM_CAD_Design":           ["urban_drone", "space_shuttle", "eco_car"],
    # eHealth products
    "eHealth365_CAD_Design":     ["health_key_ultra", "health_band_neuro", "health_ring", "health_lab"],
}


def run_sim(script_path: Path) -> tuple[int, str, str, float]:
    """Run a simulation script and return (returncode, stdout, stderr, elapsed_s)."""
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True, timeout=60,
    )
    elapsed = time.perf_counter() - start
    return result.returncode, result.stdout, result.stderr, elapsed


def discover_sims(ecad_root: Path, division_filter: str | None) -> list[tuple[str, str, Path]]:
    """Walk ecad_root and find all power_budget_sim.py files."""
    found: list[tuple[str, str, Path]] = []
    for division, products in DIVISIONS.items():
        if division_filter and division != division_filter:
            continue
        for product in products:
            sim = ecad_root / division / product / "simulation" / "power_budget_sim.py"
            if sim.exists():
                found.append((division, product, sim))
    return found


def print_github_summary(results: list[tuple]) -> None:
    """Print a GitHub Actions Step Summary markdown table."""
    passed = sum(1 for r in results if r[2] == "PASS")
    failed = sum(1 for r in results if r[2] == "FAIL")
    print("## EmbeddedOS eBuild — CAD Simulation Report\n")
    print(f"**{len(results)} products** | ✅ {passed} passed | ❌ {failed} failed\n")
    print("| Division | Product | Status | Time | Key Output |")
    print("|---|---|---|---|---|")
    for div, prod, status, elapsed_ms, first_line in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"| `{div}` | `{prod}` | {icon} {status} | {elapsed_ms:.0f}ms | {first_line} |")


def main() -> int:
    parser = argparse.ArgumentParser(description="EmbeddedOS eBuild CAD Simulation Runner")
    parser.add_argument("--ecad-root", type=Path,
                        help="Path to eCAD-Hardware-Products checkout")
    parser.add_argument("--division", type=str, default=None,
                        help="Run only this division (e.g. eAerospace_CAD_Design)")
    parser.add_argument("--github-summary", action="store_true",
                        help="Output GitHub Actions Step Summary markdown")
    args = parser.parse_args()

    # Resolve eCAD root
    ecad_root: Path | None = args.ecad_root
    if ecad_root is None:
        # Try common relative paths
        for candidate in [
            Path("../eCAD-Hardware-Products"),
            Path("../../eCAD-Hardware-Products"),
            Path("/home/ubuntu/repo_merge/eCAD-Hardware-Products"),
        ]:
            if candidate.exists():
                ecad_root = candidate.resolve()
                break

    results: list[tuple[str, str, str, float, str]] = []
    total_start = time.perf_counter()

    if ecad_root:
        sims = discover_sims(ecad_root, args.division)
        if not sims:
            print(f"{YELLOW}⚠  No simulation files found under {ecad_root}{RESET}")
            return 0

        print(f"\n{BOLD}EmbeddedOS eBuild — CAD Product Simulation Runner{RESET}")
        print(f"eCAD root: {ecad_root}")
        print(f"Products found: {len(sims)}\n")

        for division, product, sim_path in sims:
            rc, stdout, stderr, elapsed = run_sim(sim_path)
            status = "PASS" if rc == 0 else "FAIL"
            first_line = stdout.strip().split("\n")[0] if stdout.strip() else "(no output)"
            results.append((division, product, status, elapsed * 1000, first_line))
            icon = f"{GREEN}✅{RESET}" if status == "PASS" else f"{RED}❌{RESET}"
            print(f"  {icon} {division:<35} {product:<28} {elapsed*1000:>5.0f}ms  {first_line}")
    else:
        # No checkout — run the pytest suite which has inline simulations
        print(f"\n{BOLD}EmbeddedOS eBuild — CAD Simulation (inline mode){RESET}")
        print("No eCAD-Hardware-Products checkout found — running inline simulations via pytest\n")
        rc = subprocess.run(
            [sys.executable, "-m", "pytest",
             "tests/simulation/test_ecad_product_simulations.py", "-v", "-s",
             "--tb=short"],
            capture_output=False,
        ).returncode
        return rc

    total_elapsed = time.perf_counter() - total_start
    passed = sum(1 for r in results if r[2] == "PASS")
    failed = sum(1 for r in results if r[2] == "FAIL")

    if args.github_summary:
        print_github_summary(results)
    else:
        print()
        print("=" * 90)
        print(f"  {BOLD}EmbeddedOS eBuild CAD Simulation Summary{RESET}")
        print("=" * 90)
        print(f"  Total products : {len(results)}")
        print(f"  {GREEN}✅ Passed{RESET}       : {passed}")
        print(f"  {RED}❌ Failed{RESET}       : {failed}")
        print(f"  ⏱  Build time   : {total_elapsed*1000:.0f}ms")
        print("=" * 90)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
