#!/usr/bin/env python3
"""Generate a fabrication readiness report for a KiCad schematic (pre-PCB layout stage)."""
import re
import sys
import json
import os

def fab_readiness(sch_path, out_dir):
    design = os.path.basename(os.path.dirname(sch_path))
    os.makedirs(out_dir, exist_ok=True)
    try:
        with open(sch_path) as f:
            content = f.read()
        nets = re.findall(r'\(net \d+ "([^"]+)"', content)
        comps = re.findall(r'\(lib_id "([^"]+)"', content)
        report = {
            "design": design,
            "schematic": sch_path,
            "nets": len(set(nets)),
            "components": len(comps),
            "status": "schematic_only",
            "next_step": "Create .kicad_pcb layout for Gerber export",
            "fab_ready": False
        }
    except Exception as e:
        report = {
            "design": design,
            "schematic": sch_path,
            "status": "error",
            "error": str(e),
            "fab_ready": False
        }

    out_file = os.path.join(out_dir, f"{design}_fab_readiness.json")
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report))
    return report

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: gerber-fab-readiness.py <schematic.kicad_sch> <output_dir>")
        sys.exit(1)
    fab_readiness(sys.argv[1], sys.argv[2])
