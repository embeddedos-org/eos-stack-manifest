#!/usr/bin/env node
/**
 * stats.mjs — Print a human-readable summary of the EoS manifest.
 */
import { readFileSync } from 'fs';

const manifest = JSON.parse(readFileSync('manifest.json', 'utf8'));
const { projects } = manifest;

const byPlatform = {};
const byTier = {};
const byLang = {};
let eosCount = 0;

for (const p of projects) {
  byPlatform[p.platform] = (byPlatform[p.platform] || 0) + 1;
  byTier[p.tier] = (byTier[p.tier] || 0) + 1;
  const lang = p.language || 'Unknown';
  byLang[lang] = (byLang[lang] || 0) + 1;
  if (p.eosConfig) eosCount++;
}

console.log('\n📊 EoS Stack Manifest — Statistics\n');
console.log(`   Total repos:     ${projects.length}`);
console.log(`   EoS-integrated:  ${eosCount}`);
console.log(`   Last updated:    ${manifest.lastUpdated || manifest.generatedAt?.split('T')[0]}\n`);

console.log('   By Platform:');
for (const [k, v] of Object.entries(byPlatform).sort((a,b) => b[1]-a[1])) {
  const bar = '█'.repeat(v);
  console.log(`     ${k.padEnd(12)} ${String(v).padStart(2)}  ${bar}`);
}

console.log('\n   By Tier:');
const TIER_NAMES = { 1: 'Core OS', 2: 'Platform Tools', 3: 'Applications', 4: 'Web & Docs', 5: 'Meta' };
for (const t of [1,2,3,4,5]) {
  const v = byTier[t] || 0;
  console.log(`     Tier ${t} (${TIER_NAMES[t]})  ${String(v).padStart(2)}`);
}

console.log('\n   By Language:');
for (const [k, v] of Object.entries(byLang).sort((a,b) => b[1]-a[1])) {
  console.log(`     ${k.padEnd(14)} ${v}`);
}
console.log('');
