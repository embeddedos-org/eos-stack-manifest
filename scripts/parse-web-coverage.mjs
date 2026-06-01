#!/usr/bin/env node
import { readFileSync, existsSync } from 'fs';
if (!existsSync('./coverage/coverage-summary.json')) {
  console.log('No coverage data generated');
  process.exit(0);
}
const c = JSON.parse(readFileSync('./coverage/coverage-summary.json', 'utf8')).total;
console.log('| Metric | Value |');
console.log('|--------|-------|');
console.log(`| Lines | ${c.lines.pct}% (${c.lines.covered}/${c.lines.total}) |`);
console.log(`| Branches | ${c.branches.pct}% (${c.branches.covered}/${c.branches.total}) |`);
console.log(`| Functions | ${c.functions.pct}% (${c.functions.covered}/${c.functions.total}) |`);
const ok = c.lines.pct >= 100;
console.log(`| Status | ${ok ? '✅ 100%' : '⚠️ ' + c.lines.pct + '%'} |`);
