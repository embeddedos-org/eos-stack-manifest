#!/usr/bin/env node
/**
 * validate-schema.mjs — Validates manifest.json against the JSON schema.
 */
import { readFileSync } from 'fs';

const REQUIRED_FIELDS = ['name', 'repo', 'path', 'type', 'platform', 'tier', 'description',
  'language', 'defaultBranch', 'testCommand', 'buildCommand', 'releaseTarget'];

const VALID_PLATFORMS = ['firmware', 'desktop', 'mobile', 'web', 'backend', 'hardware', 'ai', 'meta', 'unknown'];
const VALID_TIERS = [1, 2, 3, 4, 5];

let errors = 0;

function fail(msg) {
  console.error(`  ❌ ${msg}`);
  errors++;
}

const manifest = JSON.parse(readFileSync('manifest.json', 'utf8'));

console.log('\n🔎 Validating manifest.json...\n');

if (!manifest.version) fail('Missing top-level "version" field');
if (!manifest.org) fail('Missing top-level "org" field');
if (!Array.isArray(manifest.projects)) fail('Missing "projects" array');

const names = new Set();
for (const p of manifest.projects || []) {
  // Check for duplicate names
  if (names.has(p.name)) fail(`Duplicate project name: ${p.name}`);
  names.add(p.name);

  // Check required fields
  for (const f of REQUIRED_FIELDS) {
    if (p[f] === undefined || p[f] === null) fail(`${p.name}: missing required field "${f}"`);
  }

  // Check platform validity
  if (!VALID_PLATFORMS.includes(p.platform)) fail(`${p.name}: invalid platform "${p.platform}"`);

  // Check tier validity
  if (!VALID_TIERS.includes(p.tier)) fail(`${p.name}: invalid tier ${p.tier} (must be 1-5)`);

  // Check repo format
  if (p.repo && !p.repo.includes('/')) fail(`${p.name}: repo must be "org/name" format`);
}

if (errors === 0) {
  console.log(`  ✅ manifest.json is valid (${manifest.projects.length} projects, 0 errors)\n`);
} else {
  console.error(`\n  Found ${errors} error(s) in manifest.json\n`);
  process.exit(1);
}
