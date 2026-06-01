#!/usr/bin/env node
/**
 * discover.mjs — EoS Stack Manifest Auto-Discovery
 *
 * Queries the GitHub API for all repos in embeddedos-org, detects each
 * repo's platform/stack/tier, and updates manifest.json + build-matrix.json.
 *
 * Usage:
 *   node scripts/discover.mjs              # live update
 *   node scripts/discover.mjs --dry-run    # print only, no file writes
 */

import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';

const DRY_RUN = process.argv.includes('--dry-run');
const TOKEN = process.env.GH_TOKEN || process.env.GITHUB_TOKEN || '';
const ORG = 'embeddedos-org';
const MANIFEST_PATH = 'manifest.json';
const MATRIX_PATH = 'build-matrix.json';

// Meta repos that should never appear in the build matrix
const META_REPOS = new Set(['.github', 'embeddedos-org', 'eos-stack-manifest']);

// Language → platform mapping
const LANG_PLATFORM = {
  C: 'firmware', 'C++': 'firmware', Assembly: 'firmware',
  Go: 'backend', Rust: 'firmware',
  Python: 'desktop', TypeScript: 'web', JavaScript: 'web',
  HTML: 'web', CSS: 'web', Makefile: 'firmware',
  Swift: 'mobile', Kotlin: 'mobile', Dart: 'mobile',
};

// Repo name patterns → tier
function detectTier(name) {
  if (['eos', 'eBoot', 'eAI', 'eDB', 'eIPC', 'eosllm', 'ebuild'].includes(name)) return 1;
  if (['EoSim', 'EoStudio', 'eVera', 'eBrowser', 'eCAD-Hardware-Products'].includes(name)) return 2;
  if (['eNI', 'HEALTH-BAND-Neuro', 'HealthKey-Ulta', 'eOffice', 'eApps'].includes(name)) return 3;
  if (['www.embeddedos.org', 'embeddedos-org.github.io'].includes(name)) return 4;
  return 5;
}

// Detect build stack from repo topics + language
function detectStack(repo) {
  const lang = repo.language || '';
  const topics = repo.topics || [];
  const stacks = [];

  if (lang === 'C' || lang === 'C++') stacks.push('c', 'cmake');
  if (lang === 'Python') stacks.push('python');
  if (lang === 'Go') stacks.push('go');
  if (lang === 'TypeScript') stacks.push('typescript');
  if (lang === 'JavaScript') stacks.push('javascript');
  if (topics.includes('electron')) stacks.push('electron');
  if (topics.includes('react')) stacks.push('react');
  if (topics.includes('fastapi')) stacks.push('fastapi');
  if (topics.includes('ollama')) stacks.push('ollama');
  if (topics.includes('qemu')) stacks.push('qemu');
  if (topics.includes('kicad')) stacks.push('kicad');
  if (topics.includes('react-native')) stacks.push('react-native');

  return [...new Set(stacks)];
}

async function fetchAllRepos() {
  const headers = TOKEN
    ? { Authorization: `token ${TOKEN}`, Accept: 'application/vnd.github.v3+json' }
    : { Accept: 'application/vnd.github.v3+json' };

  let page = 1;
  const all = [];

  while (true) {
    const url = `https://api.github.com/orgs/${ORG}/repos?per_page=100&type=all&page=${page}`;
    const res = await fetch(url, { headers });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`GitHub API error ${res.status}: ${body}`);
    }

    const repos = await res.json();
    if (!repos.length) break;
    all.push(...repos);
    if (repos.length < 100) break;
    page++;
  }

  return all;
}

async function main() {
  console.log(`\n🔍 EoS Stack Manifest — Auto-Discovery`);
  console.log(`   Org: ${ORG}  |  Mode: ${DRY_RUN ? 'DRY RUN' : 'LIVE UPDATE'}\n`);

  const repos = await fetchAllRepos();
  console.log(`   Found ${repos.length} repos in ${ORG}\n`);

  // Load existing manifest to preserve hand-crafted fields
  let existing = {};
  try {
    const m = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8'));
    existing = Object.fromEntries((m.projects || []).map(p => [p.name, p]));
  } catch {}

  const projects = [];
  const buildRepos = [];

  for (const repo of repos.sort((a, b) => a.name.localeCompare(b.name))) {
    const name = repo.name;
    const isMeta = META_REPOS.has(name);
    const lang = repo.language || '';
    const platform = LANG_PLATFORM[lang] || (isMeta ? 'meta' : 'unknown');
    const tier = detectTier(name);
    const stack = detectStack(repo);
    const ex = existing[name] || {};

    const project = {
      name,
      repo: `${ORG}/${name}`,
      path: ex.path || `${platform}/${name}`,
      type: ex.type || platform,
      platform,
      stack: ex.stack?.length ? ex.stack : stack,
      tier,
      description: repo.description || ex.description || '',
      language: lang,
      defaultBranch: repo.default_branch || 'master',
      testCommand: ex.testCommand || 'echo "No test command defined"',
      buildCommand: ex.buildCommand || 'echo "No build command defined"',
      installCommand: ex.installCommand || 'echo "No install command defined"',
      releaseTarget: ex.releaseTarget || [],
      ciRunner: ex.ciRunner || 'ubuntu-latest',
      requiresSecrets: ex.requiresSecrets || [],
      tags: [...new Set([...(ex.tags || []), ...(repo.topics || [])])],
      eosConfig: ex.eosConfig ?? (tier <= 2),
      archived: repo.archived || false,
      stars: repo.stargazers_count || 0,
      updatedAt: repo.updated_at,
    };

    projects.push(project);

    if (!isMeta && !repo.archived) {
      buildRepos.push(name);
    }
  }

  // Print summary table
  console.log('  Tier  Name                            Platform     Language');
  console.log('  ────  ──────────────────────────────  ───────────  ────────');
  for (const p of projects) {
    const tier = String(p.tier).padEnd(4);
    const name = p.name.padEnd(32);
    const platform = p.platform.padEnd(11);
    console.log(`  ${tier}  ${name}  ${platform}  ${p.language || '—'}`);
  }
  console.log(`\n  Total: ${projects.length} repos | Build matrix: ${buildRepos.length} repos\n`);

  if (DRY_RUN) {
    console.log('  ✅ Dry run complete — no files written.\n');
    return;
  }

  // Write manifest.json
  const manifest = {
    version: '1.0.0',
    org: ORG,
    generatedAt: new Date().toISOString(),
    totalRepos: projects.length,
    lastUpdated: new Date().toISOString().split('T')[0],
    defaults: {
      branch: 'master',
      nodeVersion: '22',
      pythonVersion: '3.12',
      ciRunner: 'ubuntu-latest',
    },
    projects,
  };

  writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n');
  console.log(`  ✅ Written: ${MANIFEST_PATH}`);

  // Write build-matrix.json
  const matrix = {
    repos: buildRepos,
    total: buildRepos.length,
    updated: new Date().toISOString().split('T')[0],
    note: 'Auto-managed — do not edit manually. Add repos to EXCLUDE list in workflow to skip.',
    excluded: [...META_REPOS],
  };

  writeFileSync(MATRIX_PATH, JSON.stringify(matrix, null, 2) + '\n');
  console.log(`  ✅ Written: ${MATRIX_PATH}\n`);
}

main().catch(err => {
  console.error('❌ Discovery failed:', err.message);
  process.exit(1);
});
