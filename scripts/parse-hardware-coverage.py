#!/usr/bin/env python3
"""Parse pytest coverage output and print a Markdown summary for GitHub Step Summary."""
import re
import sys
import os

def parse_coverage(output_file):
    try:
        with open(output_file) as f:
            txt = f.read()
    except FileNotFoundError:
        print("No pytest output found.")
        return

    # Extract coverage total
    m = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', txt)
    cov = m.group(1) if m else "?"

    # Count passed/failed/error
    passed = len(re.findall(r' PASSED', txt))
    failed = len(re.findall(r' FAILED', txt))
    errors = len(re.findall(r' ERROR', txt))

    print(f"| eCAD-Hardware-Products | pytest | {cov}% | {passed} passed / {failed} failed / {errors} errors | {'✓' if failed == 0 else '✗'} |")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output/sim/pytest_output.txt"
    parse_coverage(output_file)
