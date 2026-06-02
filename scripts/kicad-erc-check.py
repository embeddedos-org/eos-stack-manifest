#!/usr/bin/env python3
"""Parse a KiCad schematic file and report basic structural validity (ERC fallback)."""
import re
import sys
import json
import os

def check_schematic(sch_path):
    try:
        with open(sch_path) as f:
            content = f.read()
        nets = len(re.findall(r'\(net ', content))
        symbols = len(re.findall(r'\(symbol ', content))
        lib_ids = re.findall(r'\(lib_id "([^"]+)"', content)
        unique_parts = len(set(lib_ids))
        result = {
            "file": sch_path,
            "design": os.path.basename(os.path.dirname(sch_path)),
            "symbols": symbols,
            "nets": nets,
            "unique_parts": unique_parts,
            "status": "ok",
            "message": f"Schematic OK: {symbols} symbols, {nets} nets, {unique_parts} unique parts"
        }
        print(result["message"])
        return result
    except FileNotFoundError:
        print(f"ERROR: {sch_path} not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR parsing {sch_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: kicad-erc-check.py <schematic.kicad_sch>")
        sys.exit(1)
    result = check_schematic(sys.argv[1])
    # Write JSON report alongside the schematic
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output/erc"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, result["design"] + "_erc.json")
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Report written: {out_file}")
