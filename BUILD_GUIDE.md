# EoS Stack — Build Guide

This document explains how to build every component of the EmbeddedOS stack from source, either individually or as a complete system using the manifest.

---

## Prerequisites

| Tool | Version | Required For |
|------|---------|-------------|
| Git | 2.40+ | All repos |
| Node.js | 22+ | Web, Electron, scripts |
| Python | 3.12+ | eVera, EoSim, EoStudio, eDB |
| Go | 1.22+ | eIPC |
| GCC / ARM toolchain | 13+ | eos, eBoot, eAI, eNI |
| CMake | 3.28+ | Firmware repos |
| Docker | 24+ | Containerized builds |
| KiCad | 7+ | eCAD-Hardware-Products |
| QEMU | 8+ | EoSim |
| Electron Builder | 24+ | Desktop apps |

Install all prerequisites on Ubuntu 22.04+:

```bash
# Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt-get install -y nodejs

# Python 3.12
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

# Go 1.22
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# ARM toolchain
sudo apt-get install -y gcc-arm-none-eabi binutils-arm-none-eabi

# CMake
sudo apt-get install -y cmake ninja-build

# QEMU
sudo apt-get install -y qemu-system-arm qemu-system-x86

# KiCad
sudo apt-get install -y kicad
```

---

## Building the Full Stack

```bash
git clone https://github.com/embeddedos-org/eos-stack-manifest.git
cd eos-stack-manifest
npm install
bash scripts/build-all.sh
```

This clones every repo in the manifest into `~/eos-build/`, installs dependencies, builds, and runs tests.

---

## Building Individual Tiers

### Tier 1 — Core OS

```bash
bash scripts/build-all.sh --tier 1
```

Builds: `eos` (RTOS), `eBoot` (bootloader), `eAI` (AI layer), `eDB` (database), `eIPC` (IPC), `eosllm` (on-device LLM), `ebuild` (build tool).

### Tier 2 — Platform Tools

```bash
bash scripts/build-all.sh --tier 2
```

Builds: `EoSim` (QEMU simulator), `EoStudio` (IDE), `eVera` (AI agent), `eBrowser`, `eCAD-Hardware-Products`.

### Tier 3 — Applications

```bash
bash scripts/build-all.sh --tier 3
```

Builds: `eOffice`, `eApps`, `HEALTH-BAND-Neuro`, `HealthKey-Ulta`, `eNI`.

---

## Building a Single Repo

```bash
bash scripts/build-all.sh --repo eVera
```

---

## Building eVera (AI Agent)

```bash
git clone https://github.com/embeddedos-org/eVera.git
cd eVera
bash setup.sh                          # Linux/macOS
# or: powershell -f setup.ps1          # Windows

# Start the server
python3 main.py --mode server

# Build the desktop installer
cd electron && npm install && npm run build:linux
```

---

## Building the VS Code Extension

```bash
cd eVera/vscode-extension
npm install
npm run compile
npx vsce package
# Produces: evera-ai-*.vsix
code --install-extension evera-ai-*.vsix
```

---

## CI Build (GitHub Actions)

Every push to `master` triggers the `unified-build.yml` workflow automatically. To trigger a release build manually:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The CI will build all platforms and attach artifacts to the GitHub Release.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `arm-none-eabi-gcc: not found` | ARM toolchain missing | `sudo apt-get install gcc-arm-none-eabi` |
| `pyinstaller: command not found` | PyInstaller not installed | `pip install pyinstaller` |
| `electron-builder: command not found` | Electron deps missing | `cd electron && npm install` |
| `cmake: not found` | CMake missing | `sudo apt-get install cmake` |
| `GH_TOKEN not set` | Missing GitHub token | `export GH_TOKEN=your_token` |
| Build fails on macOS | Xcode tools missing | `xcode-select --install` |
