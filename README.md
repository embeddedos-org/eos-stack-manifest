# eos-stack-manifest

**EmbeddedOS Unified Build, Test & Release Manifest**

[![Unified Build](https://github.com/embeddedos-org/eos-stack-manifest/actions/workflows/unified-build.yml/badge.svg)](https://github.com/embeddedos-org/eos-stack-manifest/actions/workflows/unified-build.yml)
[![Repos](https://img.shields.io/badge/repos-22-blue)](manifest.json)
[![Platforms](https://img.shields.io/badge/platforms-firmware%20%7C%20desktop%20%7C%20mobile%20%7C%20web%20%7C%20hardware-green)](manifest.json)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## What is this?

`eos-stack-manifest` is the **single source of truth** for building, testing, and releasing every project in the [embeddedos-org](https://github.com/embeddedos-org) GitHub organization. It is modeled after the [AGL Unified Manifest](https://github.com/AmericanGroupLLC/agl-manifest) pattern but built specifically for the EmbeddedOS stack — covering firmware, desktop tools, AI agents, mobile apps, web services, and hardware designs.

One manifest file. One CI workflow. Every repo. Every platform.

---

## The EoS Stack

| Tier | Projects | Description |
|------|----------|-------------|
| **1 — Core OS** | `eos`, `eBoot`, `eAI`, `eDB`, `eIPC`, `eosllm`, `ebuild` | RTOS, bootloader, AI layer, database, IPC, on-device LLM, build tool |
| **2 — Platform Tools** | `EoSim`, `EoStudio`, `eVera`, `eBrowser`, `eCAD` | Simulator, IDE, AI agent, browser, hardware CAD |
| **3 — Applications** | `eOffice`, `eApps`, `HEALTH-BAND-Neuro`, `HealthKey-Ulta`, `eNI` | Office suite, app store, health wearable, neural interface |
| **4 — Web & Docs** | `www.embeddedos.org`, `embeddedos-org.github.io` | Foundation website, developer docs |
| **5 — Meta** | `.github`, `eos-stack-manifest` | Org config, this manifest |

---

## Quick Start

```bash
git clone https://github.com/embeddedos-org/eos-stack-manifest.git
cd eos-stack-manifest
npm install

# Build everything
bash scripts/build-all.sh

# Build a specific tier
bash scripts/build-all.sh --tier 1

# Build a specific repo
bash scripts/build-all.sh --repo eVera

# Dry run (validate only, no builds)
bash scripts/build-all.sh --dry-run

# Sync all repos to latest master
bash scripts/sync.sh

# Release all repos with a new version tag
GH_TOKEN=your_token bash scripts/release-all.sh v1.0.0

# Print manifest statistics
node scripts/stats.mjs

# Auto-discover and update manifest from GitHub API
node scripts/discover.mjs
```

---

## Manifest Structure

Each project entry in [`manifest.json`](manifest.json):

```json
{
  "name": "eVera",
  "repo": "embeddedos-org/eVera",
  "platform": "desktop",
  "stack": ["python", "fastapi", "electron", "react", "ollama"],
  "tier": 2,
  "defaultBranch": "master",
  "testCommand": "pytest tests/",
  "buildCommand": "pyinstaller vera.spec && cd electron && npm run build:linux",
  "installCommand": "pip install -r requirements.txt && cd electron && npm install",
  "releaseTarget": ["exe", "dmg", "appimage", "deb", "apk", "vsix"],
  "eosConfig": true
}
```

---

## CI/CD Pipeline

The [`unified-build.yml`](.github/workflows/unified-build.yml) runs on every push to `master`, nightly at 03:00 UTC, and on every `v*` tag push.

```
push to master  →  discover + validate
                         ↓
         ┌───────────────┼────────────────┬─────────────┐
   build-firmware  build-python    build-go      build-web
         └───────────────┼────────────────┴─────────────┘
                   build-hardware
                         ↓ (on v* tag only)
                      release
               (GitHub Release + all artifacts)
```

---

## Scripts Reference

| Script | Description |
|--------|-------------|
| `scripts/discover.mjs` | Auto-discovers all org repos, detects platform/stack/tier, updates `manifest.json` |
| `scripts/validate-schema.mjs` | Validates `manifest.json` — runs in CI on every push |
| `scripts/stats.mjs` | Prints repo summary by platform, tier, and language |
| `scripts/build-all.sh` | Builds all repos locally (supports `--tier`, `--repo`, `--dry-run`) |
| `scripts/sync.sh` | Syncs all repos to latest master |
| `scripts/release-all.sh` | Tags all repos with a version and triggers their CI release jobs |
| `scripts/generate-release-docs.mjs` | Generates `RELEASE.md` for GitHub Releases |

---

## Fork Support

Fork this repo and set `source_org` in `manifest-config.json` to build the entire EoS stack from your own organization. Set `GH_TOKEN` in your fork's secrets for cross-org access.

---

## Comparison with agl-manifest

| Feature | agl-manifest | eos-stack-manifest |
|---------|-------------|-------------------|
| Auto-discovery | Manual | **Automatic via GitHub API** |
| Schema validation | None | **JSON schema + CI validation** |
| Local build script | None | **`build-all.sh` with tier/repo filters** |
| Release automation | Manual | **`release-all.sh` tags all repos** |
| Fork support | No | **Yes — `manifest-config.json`** |
| Stats reporting | None | **`stats.mjs`** |
| Release notes | Manual | **Auto-generated from manifest** |
| Nightly builds | No | **Yes — 03:00 UTC** |
| Hardware support | No | **Yes — KiCad/Gerber** |

---

## License

MIT — see [LICENSE](LICENSE).

*Maintained by the [EmbeddedOS Foundation](https://www.embeddedos.org)*
