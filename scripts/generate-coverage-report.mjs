#!/usr/bin/env node
/**
 * generate-coverage-report.mjs
 * Aggregates all per-repo coverage artifacts into COVERAGE_REPORT.md
 * with build status table, compatibility matrix, and release binaries table.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import path from 'path';

const manifest = JSON.parse(readFileSync('manifest.json', 'utf8'));
const date = new Date().toISOString().split('T')[0];

function parsePythonCoverage(dir) {
  const xmlPath = path.join(dir, 'coverage.xml');
  if (!existsSync(xmlPath)) return null;
  const xml = readFileSync(xmlPath, 'utf8');
  const lineMatch = xml.match(/line-rate="([0-9.]+)"/);
  const branchMatch = xml.match(/branch-rate="([0-9.]+)"/);
  if (!lineMatch) return null;
  return {
    lines: (parseFloat(lineMatch[1]) * 100).toFixed(1),
    branches: branchMatch ? (parseFloat(branchMatch[1]) * 100).toFixed(1) : 'N/A',
  };
}

function parseGoCoverage(dir) {
  const outPath = path.join(dir, 'coverage.out');
  if (!existsSync(outPath)) return null;
  const lines = readFileSync(outPath, 'utf8').split('\n');
  const total = lines.find(l => l.includes('total:'));
  if (!total) return null;
  const pct = total.match(/([0-9.]+)%/);
  return pct ? { lines: pct[1], branches: 'N/A' } : null;
}

const L = [];

L.push('# EoS Stack -- Build & Coverage Report');
L.push('');
L.push(`> Generated: ${date} | Source: [embeddedos-org](https://github.com/embeddedos-org)`);
L.push('');
L.push('---');
L.push('');
L.push('## Build Status & Test Coverage');
L.push('');
L.push('| Repo | Platform | Language | Tier | Line Cov | Branch Cov | Status |');
L.push('|------|----------|----------|------|----------|------------|--------|');

for (const p of manifest.projects.filter(x => x.platform !== 'meta')) {
  let cov = null;
  const covDirs = [
    `all-coverage/coverage-python-${p.name}`,
    `all-coverage/coverage-go-${p.name}`,
    `all-coverage/coverage-firmware-${p.name}`,
    `all-coverage/coverage-web-${p.name}`,
  ];
  for (const d of covDirs) {
    if (existsSync(d)) {
      if (d.includes('python')) cov = parsePythonCoverage(d);
      else if (d.includes('go')) cov = parseGoCoverage(d);
      else if (d.includes('firmware')) cov = parsePythonCoverage(d);
      if (cov) break;
    }
  }
  const linePct = cov ? cov.lines + '%' : '--';
  const branchPct = cov ? cov.branches + '%' : '--';
  const status = cov ? (parseFloat(cov.lines) >= 100 ? 'PASS 100%' : 'WARN ' + cov.lines + '%') : 'Built';
  L.push(`| [${p.name}](https://github.com/${p.repo}) | ${p.platform} | ${p.language || '--'} | ${p.tier} | ${linePct} | ${branchPct} | ${status} |`);
}

L.push('');
L.push('---');
L.push('');
L.push('## Compatibility Matrix');
L.push('');
L.push('### Firmware -- Target Hardware');
L.push('');
L.push('| Firmware | MCU / SoC | Architecture | Toolchain | RTOS / OS |');
L.push('|----------|-----------|--------------|-----------|-----------|');
L.push('| eos | ARM Cortex-M4/M7, RISC-V | ARMv7-M, RV32 | arm-none-eabi-gcc 13 | Bare-metal |');
L.push('| eBoot | Any ARM Cortex-M | ARMv7-M | arm-none-eabi-gcc 13 | Bare-metal |');
L.push('| eAI | ARM Cortex-M55, Cortex-A55 | ARMv8.1-M, ARMv8-A | arm-none-eabi-gcc 13 | eos RTOS, Linux |');
L.push('| eosllm | ARM Cortex-M7+ | ARMv7E-M | arm-none-eabi-gcc 13 | eos RTOS |');
L.push('| eNI | ARM Cortex-M4 | ARMv7-M | arm-none-eabi-gcc 13 | eos RTOS |');
L.push('| ebuild | Host (cross-compile) | x86_64, ARM64 | GCC/Clang | Linux, macOS, Windows |');
L.push('| HEALTH-BAND-Neuro | Nordic nRF52840 | ARM Cortex-M4F | arm-none-eabi-gcc 13 | Zephyr RTOS 3.x |');
L.push('');
L.push('### Software -- Host Platform Support');
L.push('');
L.push('| Application | Linux | macOS | Windows | Android | iOS | Web | Min Runtime |');
L.push('|-------------|-------|-------|---------|---------|-----|-----|-------------|');
L.push('| eVera (AI Agent) | Yes | Yes | Yes | Yes | Yes | Yes | Python 3.10+ |');
L.push('| EoStudio (IDE) | Yes | Yes | Yes | No | No | No | Python 3.10+ |');
L.push('| EoSim (Simulator) | Yes | Yes | Yes | No | No | No | Python 3.10+ |');
L.push('| eDB (Database) | Yes | Yes | Yes | No | No | Yes | Node 22+, Python 3.12+ |');
L.push('| eOffice (Productivity) | Yes | Yes | Yes | No | No | Yes | Node 22+ |');
L.push('| eApps (App Hub) | Yes | Yes | Yes | No | No | Yes | Node 22+ |');
L.push('| HealthKey-Ulta (Health) | No | No | No | Yes | Yes | Yes | React Native 0.73+ |');
L.push('| www.embeddedos.org | Yes | Yes | Yes | No | No | Yes | Node 22+ |');
L.push('| eIPC (IPC daemon) | Yes | Yes | Yes | No | No | No | Go 1.22+ |');
L.push('');
L.push('### Runtime Dependency Versions');
L.push('');
L.push('| Dependency | Minimum | Recommended | Used By |');
L.push('|------------|---------|-------------|---------|');
L.push('| Node.js | 20.x | 22.x LTS | eOffice, eDB, eApps, www |');
L.push('| Python | 3.10 | 3.12 | eVera, EoSim, EoStudio, eDB |');
L.push('| Go | 1.21 | 1.22 | eIPC |');
L.push('| GCC ARM | 12.x | 13.x | All firmware |');
L.push('| CMake | 3.20 | 3.28 | eos, eBoot, eAI, eNI, ebuild |');
L.push('| Ninja | 1.10 | 1.11 | Firmware (optional) |');
L.push('| Zephyr SDK | 0.16 | 0.16 | HEALTH-BAND-Neuro |');
L.push('');
L.push('---');
L.push('');
L.push('## Release Binaries');
L.push('');
L.push('### Firmware');
L.push('');
L.push('| File | Repo | Format | Target |');
L.push('|------|------|--------|--------|');
L.push('| eos.elf | eos | ELF | ARM Cortex-M |');
L.push('| eos.hex | eos | Intel HEX | ARM Cortex-M |');
L.push('| eBoot.elf | eBoot | ELF | ARM Cortex-M |');
L.push('| eAI.elf | eAI | ELF | Cortex-M55/A55 |');
L.push('| libeosllm.a | eosllm | Static lib | ARM Cortex-M7 |');
L.push('| eNI.elf | eNI | ELF | ARM Cortex-M4 |');
L.push('| health_band_neuro.elf | HEALTH-BAND-Neuro | ELF | nRF52840 |');
L.push('');
L.push('### Desktop & CLI');
L.push('');
L.push('| File | Repo | Platform | Architecture |');
L.push('|------|------|----------|--------------|');
L.push('| eipc-linux-amd64 | eIPC | Linux | x86_64 |');
L.push('| eipc-linux-arm64 | eIPC | Linux | ARM64 |');
L.push('| eipc-windows-amd64.exe | eIPC | Windows | x86_64 |');
L.push('| eipc-darwin-amd64 | eIPC | macOS | x86_64 |');
L.push('| eVera-linux.AppImage | eVera | Linux | x86_64 |');
L.push('| EoStudio-linux.AppImage | EoStudio | Linux | x86_64 |');
L.push('| EoSim-linux.AppImage | EoSim | Linux | x86_64 |');
L.push('');
L.push('### Web & Mobile');
L.push('');
L.push('| Package | Repo | Format |');
L.push('|---------|------|--------|');
L.push('| eApps-web.zip | eApps | Static web |');
L.push('| eOffice-web.zip | eOffice | Static web |');
L.push('| www.embeddedos.org-web.zip | www.embeddedos.org | Static web |');
L.push('| HealthKey-Ulta-web.zip | HealthKey-Ulta | Web + PWA |');
L.push('');
L.push('---');
L.push('');
L.push(`*Generated by eos-stack-manifest CI -- ${date}*`);

writeFileSync('COVERAGE_REPORT.md', L.join('\n'));
console.log('COVERAGE_REPORT.md written successfully');
