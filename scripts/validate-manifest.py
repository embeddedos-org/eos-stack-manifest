#!/usr/bin/env python3
"""Validate a browser extension manifest.json for required fields and MV3 compliance."""
import json
import sys

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "manifest.json"
    try:
        with open(path) as f:
            d = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {path}: {e}")
        sys.exit(1)

    required = ["name", "version", "manifest_version"]
    missing = [k for k in required if k not in d]
    if missing:
        print(f"FAIL: missing required fields: {missing}")
        sys.exit(1)

    mv = d.get("manifest_version", 0)
    print(f"manifest.json valid: {d['name']} v{d['version']} (MV{mv})")
    if mv < 3:
        print(f"WARNING: manifest_version {mv} — Chrome/Edge require MV3 for new submissions")
    else:
        print("MV3: compatible with Chrome, Edge, Firefox (partial)")

if __name__ == "__main__":
    main()
