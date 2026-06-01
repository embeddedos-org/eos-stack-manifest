#!/usr/bin/env python3
"""Parse coverage.xml and print a markdown table row."""
import sys, xml.etree.ElementTree as ET
try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    rate = float(root.attrib.get('line-rate', 0)) * 100
    branch = float(root.attrib.get('branch-rate', 0)) * 100
    print('| Metric | Value |')
    print('|--------|-------|')
    print(f'| Line Coverage | {rate:.1f}% |')
    print(f'| Branch Coverage | {branch:.1f}% |')
    status = '✅ 100%' if rate >= 100 else f'⚠️ {rate:.1f}%'
    print(f'| Status | {status} |')
except Exception as e:
    print(f'Coverage XML parse error: {e}')
