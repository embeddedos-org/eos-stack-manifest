#!/usr/bin/env node
/**
 * generate-release-docs.mjs — Generates RELEASE.md from manifest + GitHub API.
 *
 * Produces:
 *  - Projects table with commit SHAs
 *  - Compatibility matrix (firmware targets + software platforms)
 *  - Release binaries table
 *  - Installation instructions
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';

const TOKEN = process.env.GH_TOKEN || process.env.GITHUB_TOKEN || '';
const TAG   = process.env.RELEASE_TAG || `build-${Date.now()}`;
const ORG   = process.env.SOURCE_ORG || 'embeddedos-org';

const manifest = JSON.parse(readFileSync('manifest.json', 'utf8'));

async function getLatestCommit(repo) {
  if (!TOKEN) return null;
  try {
    const res = await fetch(
      `https://api.github.com/repos/${repo}/commits/master`,
      { headers: { Authorization: `token ${TOKEN}`, 'User-Agent': 'eos-manifest-bot' } }
    );
    if (!res.ok) return null;
    const data = await res.json();
    return {
      sha:     data.sha?.slice(0, 7),
      message: data.commit?.message?.split('\n')[0],
      date:    data.commit?.author?.date?.split('T')[0],
    };
  } catch { return null; }
}

async function main() {
  const date  = new Date().toISOString().split('T')[0];
  const lines = [];

  // ── Header ────────────────────────────────────────────────────────────────
  lines.push(`# EoS Stack Release — ${TAG}`);
  lines.push(``);
  lines.push(`> **Released:** ${date}  |  **Source org:** [${ORG}](https://github.com/${ORG})  |  **Build:** [Actions](https://github.com/${ORG}/eos-stack-manifest/actions)`);
  lines.push(``);
  lines.push(`---`);
  lines.push(``);
  lines.push(`## What is the EoS Stack?`);
  lines.push(``);
  lines.push(`The **EmbeddedOS Stack** is a complete, vertically integrated software and hardware platform.`);
  lines.push(`From bare-metal RTOS firmware to AI agents, desktop IDEs, mobile apps, and web services —`);
  lines.push(`every component is designed to work together and is built from a single manifest.`);
  lines.push(``);
  lines.push(`---`);
  lines.push(``);

  // ── Projects table ────────────────────────────────────────────────────────
  lines.push(`## Projects in This Release`);
  lines.push(``);
  lines.push(`| Tier | Name | Platform | Language | Commit | Description |`);
  lines.push(`|------|------|----------|----------|--------|-------------|`);

  const projects = manifest.projects.filter(p => p.platform !== 'meta');
  for (const p of projects) {
    const commit = await getLatestCommit(p.repo);
    const sha    = commit ? `[\`${commit.sha}\`](https://github.com/${p.repo}/commit/${commit.sha})` : '—';
    const desc   = (p.description || '').slice(0, 70);
    lines.push(`| ${p.tier} | [${p.name}](https://github.com/${p.repo}) | ${p.platform} | ${p.language || '—'} | ${sha} | ${desc} |`);
  }

  lines.push(``);
  lines.push(`---`);
  lines.push(``);

  // ── Compatibility Matrix ──────────────────────────────────────────────────
  lines.push(`## Compatibility Matrix`);
  lines.push(``);
  lines.push(`### Firmware — Target Hardware`);
  lines.push(``);
  lines.push(`| Firmware | MCU / SoC | Architecture | Toolchain | RTOS / OS |`);
  lines.push(`|----------|-----------|--------------|-----------|-----------|`);
  lines.push(`| **eos** | ARM Cortex-M4/M7, RISC-V | ARMv7-M, RV32 | arm-none-eabi-gcc 13 | Bare-metal |`);
  lines.push(`| **eBoot** | Any ARM Cortex-M | ARMv7-M | arm-none-eabi-gcc 13 | Bare-metal |`);
  lines.push(`| **eAI** | ARM Cortex-M55, Cortex-A55 | ARMv8.1-M, ARMv8-A | arm-none-eabi-gcc 13 | eos RTOS, Linux |`);
  lines.push(`| **eosllm** | ARM Cortex-M7+ | ARMv7E-M | arm-none-eabi-gcc 13 | eos RTOS |`);
  lines.push(`| **eNI** | ARM Cortex-M4 | ARMv7-M | arm-none-eabi-gcc 13 | eos RTOS |`);
  lines.push(`| **ebuild** | Host (cross-compile) | x86_64, ARM64 | GCC/Clang | Linux, macOS, Windows |`);
  lines.push(`| **HEALTH-BAND-Neuro** | Nordic nRF52840 | ARM Cortex-M4F | arm-none-eabi-gcc 13 | Zephyr RTOS 3.x |`);
  lines.push(``);
  lines.push(`### Software — Host Platform Support`);
  lines.push(``);
  lines.push(`| Application | Linux | macOS | Windows | Android | iOS | Web Browser | Min Runtime |`);
  lines.push(`|-------------|-------|-------|---------|---------|-----|-------------|-------------|`);
  lines.push(`| **eVera** (AI Agent) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Python 3.10+ |`);
  lines.push(`| **EoStudio** (IDE) | ✅ | ✅ | ✅ | — | — | — | Python 3.10+ |`);
  lines.push(`| **EoSim** (Simulator) | ✅ | ✅ | ✅ | — | — | — | Python 3.10+ |`);
  lines.push(`| **eDB** (Database) | ✅ | ✅ | ✅ | — | — | ✅ | Node 22+, Python 3.12+ |`);
  lines.push(`| **eOffice** (Productivity) | ✅ | ✅ | ✅ | — | — | ✅ | Node 22+ |`);
  lines.push(`| **eApps** (App Hub) | ✅ | ✅ | ✅ | — | — | ✅ | Node 22+ |`);
  lines.push(`| **HealthKey-Ulta** (Health) | — | — | — | ✅ | ✅ | ✅ | React Native 0.73+ |`);
  lines.push(`| **www.embeddedos.org** | ✅ | ✅ | ✅ | — | — | ✅ | Node 22+ |`);
  lines.push(`| **eIPC** (IPC daemon) | ✅ | ✅ | ✅ | — | — | — | Go 1.22+ |`);
  lines.push(``);
  lines.push(`### Runtime Dependency Versions`);
  lines.push(``);
  lines.push(`| Dependency | Minimum | Recommended | Used By |`);
  lines.push(`|------------|---------|-------------|---------|`);
  lines.push(`| Node.js | 20.x | 22.x LTS | eOffice, eDB, eApps, www |`);
  lines.push(`| Python | 3.10 | 3.12 | eVera, EoSim, EoStudio, eDB |`);
  lines.push(`| Go | 1.21 | 1.22 | eIPC |`);
  lines.push(`| GCC ARM | 12.x | 13.x | All firmware |`);
  lines.push(`| CMake | 3.20 | 3.28 | eos, eBoot, eAI, eNI, ebuild |`);
  lines.push(`| Ninja | 1.10 | 1.11 | Firmware (optional) |`);
  lines.push(`| Zephyr SDK | 0.16 | 0.16 | HEALTH-BAND-Neuro |`);
  lines.push(``);
  lines.push(`---`);
  lines.push(``);

  // ── Release Binaries Table ────────────────────────────────────────────────
  lines.push(`## Release Binaries`);
  lines.push(``);
  lines.push(`All binaries are attached to this GitHub Release as downloadable assets.`);
  lines.push(``);
  lines.push(`### Firmware Binaries`);
  lines.push(``);
  lines.push(`| File | Repo | Format | Target | Notes |`);
  lines.push(`|------|------|--------|--------|-------|`);
  lines.push(`| \`eos.elf\` | eos | ELF | ARM Cortex-M | Main RTOS kernel |`);
  lines.push(`| \`eos.hex\` | eos | Intel HEX | ARM Cortex-M | Flash-ready |`);
  lines.push(`| \`eBoot.elf\` | eBoot | ELF | ARM Cortex-M | Bootloader |`);
  lines.push(`| \`eAI.elf\` | eAI | ELF | Cortex-M55/A55 | AI inference engine |`);
  lines.push(`| \`libeosllm.a\` | eosllm | Static lib | ARM Cortex-M7 | LLM runtime |`);
  lines.push(`| \`eNI.elf\` | eNI | ELF | ARM Cortex-M4 | Neural interface |`);
  lines.push(`| \`health_band_neuro.elf\` | HEALTH-BAND-Neuro | ELF | nRF52840 | Biosensor firmware |`);
  lines.push(``);
  lines.push(`### Desktop & CLI Binaries`);
  lines.push(``);
  lines.push(`| File | Repo | Platform | Architecture |`);
  lines.push(`|------|------|----------|--------------|`);
  lines.push(`| \`eipc-linux-amd64\` | eIPC | Linux | x86_64 |`);
  lines.push(`| \`eipc-linux-arm64\` | eIPC | Linux | ARM64 |`);
  lines.push(`| \`eipc-windows-amd64.exe\` | eIPC | Windows | x86_64 |`);
  lines.push(`| \`eipc-darwin-amd64\` | eIPC | macOS | x86_64 |`);
  lines.push(`| \`eVera-linux.AppImage\` | eVera | Linux | x86_64 |`);
  lines.push(`| \`EoStudio-linux.AppImage\` | EoStudio | Linux | x86_64 |`);
  lines.push(`| \`EoSim-linux.AppImage\` | EoSim | Linux | x86_64 |`);
  lines.push(``);
  lines.push(`### Web & Mobile`);
  lines.push(``);
  lines.push(`| Package | Repo | Format | Notes |`);
  lines.push(`|---------|------|--------|-------|`);
  lines.push(`| \`eApps-web.zip\` | eApps | Static web | Deploy to any CDN |`);
  lines.push(`| \`eOffice-web.zip\` | eOffice | Static web | Deploy to any CDN |`);
  lines.push(`| \`www.embeddedos.org-web.zip\` | www.embeddedos.org | Static web | Main website |`);
  lines.push(`| \`HealthKey-Ulta-web.zip\` | HealthKey-Ulta | Web + PWA | React Native Web |`);
  lines.push(``);
  lines.push(`---`);
  lines.push(``);

  // ── Artifact types summary ────────────────────────────────────────────────
  lines.push(`## Artifact Summary`);
  lines.push(``);
  const artifactTypes = {
    'Firmware (ELF/HEX/BIN)':    ['eos', 'eBoot', 'eAI', 'eosllm', 'eNI', 'HEALTH-BAND-Neuro'],
    'Desktop (AppImage/EXE/DMG)': ['EoSim', 'EoStudio', 'eVera'],
    'CLI Binaries (multi-arch)':  ['eIPC', 'ebuild'],
    'Mobile (APK/IPA)':           ['eVera', 'HealthKey-Ulta'],
    'VS Code Extension (VSIX)':   ['eVera'],
    'Web (Static ZIP)':           ['eApps', 'www.embeddedos.org', 'eOffice', 'HealthKey-Ulta'],
    'Hardware (Gerber/BOM)':      ['eCAD-Hardware-Products'],
  };
  for (const [type, repos] of Object.entries(artifactTypes)) {
    lines.push(`**${type}:** ${repos.map(r => `\`${r}\``).join(', ')}`);
  }
  lines.push(``);
  lines.push(`---`);
  lines.push(``);

  // ── Installation ──────────────────────────────────────────────────────────
  lines.push(`## Installation`);
  lines.push(``);
  lines.push(`### eVera (AI Agent)`);
  lines.push(``);
  lines.push('```bash');
  lines.push('curl -fsSL https://raw.githubusercontent.com/embeddedos-org/eVera/master/install.sh | bash');
  lines.push('```');
  lines.push(``);
  lines.push(`### Full EoS Stack (from manifest)`);
  lines.push(``);
  lines.push('```bash');
  lines.push('git clone https://github.com/embeddedos-org/eos-stack-manifest.git');
  lines.push('cd eos-stack-manifest');
  lines.push('bash scripts/build-all.sh');
  lines.push('```');
  lines.push(``);
  lines.push(`### VS Code Extension`);
  lines.push(``);
  lines.push('```bash');
  lines.push('code --install-extension evera-ai.vsix');
  lines.push('```');
  lines.push(``);
  lines.push(`### Firmware Flashing`);
  lines.push(``);
  lines.push('```bash');
  lines.push('# Using OpenOCD');
  lines.push('openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \\');
  lines.push('  -c "program eos.elf verify reset exit"');
  lines.push('```');
  lines.push(``);
  lines.push(`---`);
  lines.push(``);
  lines.push(`## Manifest`);
  lines.push(``);
  lines.push(`The full build manifest (\`manifest.json\`) and build matrix (\`build-matrix.json\`) are attached.`);
  lines.push(`They describe every project, its build commands, release targets, and CI configuration.`);
  lines.push(``);
  lines.push(`---`);
  lines.push(``);
  // ── Append RELEASE_TABLES.md (coverage, binaries, compat, barriers) ─────
  if (existsSync('RELEASE_TABLES.md')) {
    lines.push(``);
    lines.push(`---`);
    lines.push(``);
    lines.push(`<!-- RELEASE_TABLES_START -->`);
    const tables = readFileSync('RELEASE_TABLES.md', 'utf8')
      .replace(/^# EoS Stack.*\n/, '')  // strip duplicate title
      .replace(/^> Source:.*\n/, '')    // strip duplicate source line
      .replace(/^> \*\*Legend\*\*.*\n/, '') // strip duplicate legend
      .replace(/^---\n/, '')            // strip leading hr
      .trimStart();
    lines.push(tables);
    lines.push(`<!-- RELEASE_TABLES_END -->`);
  }

  lines.push(`*Generated by [eos-stack-manifest](https://github.com/embeddedos-org/eos-stack-manifest) CI — ${date}*`);

  const content = lines.join('\n');
  writeFileSync('RELEASE.md', content);
  console.log(`✅ RELEASE.md generated (${content.length} bytes) for ${TAG}`);
}

main().catch(err => {
  console.error('❌ Release docs generation failed:', err.message);
  process.exit(1);
});
