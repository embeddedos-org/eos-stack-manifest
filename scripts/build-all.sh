#!/usr/bin/env bash
# build-all.sh — Build every repo in the EoS manifest locally.
# Usage: bash scripts/build-all.sh [--tier 1] [--repo eVera] [--dry-run]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR/.."
MANIFEST="$ROOT/manifest.json"
WORKDIR="${EOS_WORKDIR:-$HOME/eos-build}"
DRY_RUN=false
TIER_FILTER=""
REPO_FILTER=""
PASS=0
FAIL=0
SKIP=0

# ── Parse args ──────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true ;;
    --tier) TIER_FILTER="$2"; shift ;;
    --repo) REPO_FILTER="$2"; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
  shift
done

# ── Deps ─────────────────────────────────────────────────────────────────────
command -v node >/dev/null 2>&1 || { echo "❌ node is required"; exit 1; }
command -v git  >/dev/null 2>&1 || { echo "❌ git is required"; exit 1; }

echo ""
echo "🔨 EoS Stack — Build All"
echo "   Workdir: $WORKDIR"
echo "   Dry run: $DRY_RUN"
[[ -n "$TIER_FILTER" ]] && echo "   Tier filter: $TIER_FILTER"
[[ -n "$REPO_FILTER" ]] && echo "   Repo filter: $REPO_FILTER"
echo ""

mkdir -p "$WORKDIR"

# ── Read manifest ─────────────────────────────────────────────────────────────
node - <<'EOF'
const fs = require('fs');
const m = JSON.parse(fs.readFileSync('manifest.json','utf8'));
const repos = m.projects.filter(p => p.platform !== 'meta');
fs.writeFileSync('/tmp/eos_build_list.json', JSON.stringify(repos));
EOF

# ── Build each repo ───────────────────────────────────────────────────────────
while IFS= read -r line; do
  NAME=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.name)")
  REPO=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.repo)")
  TIER=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(String(d.tier))")
  INSTALL=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.installCommand)")
  BUILD=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.buildCommand)")
  TEST=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.testCommand)")
  BRANCH=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.defaultBranch)")

  # Apply filters
  [[ -n "$TIER_FILTER" && "$TIER" != "$TIER_FILTER" ]] && { ((SKIP++)); continue; }
  [[ -n "$REPO_FILTER" && "$NAME" != "$REPO_FILTER" ]] && { ((SKIP++)); continue; }

  REPO_DIR="$WORKDIR/$NAME"
  echo "── [$TIER] $NAME ──────────────────────────────────────"

  if $DRY_RUN; then
    echo "   [DRY RUN] Would clone: $REPO → $REPO_DIR"
    echo "   [DRY RUN] Install: $INSTALL"
    echo "   [DRY RUN] Build:   $BUILD"
    echo "   [DRY RUN] Test:    $TEST"
    ((PASS++))
    continue
  fi

  # Clone or pull
  if [[ -d "$REPO_DIR/.git" ]]; then
    echo "   Pulling latest..."
    git -C "$REPO_DIR" pull --ff-only origin "$BRANCH" 2>&1 | tail -1 || true
  else
    echo "   Cloning..."
    git clone --depth=1 -b "$BRANCH" "https://github.com/$REPO.git" "$REPO_DIR" 2>&1 | tail -2
  fi

  cd "$REPO_DIR"

  # Install
  echo "   Installing dependencies..."
  if ! eval "$INSTALL" > /tmp/eos_install_$NAME.log 2>&1; then
    echo "   ⚠️  Install had warnings (see /tmp/eos_install_$NAME.log)"
  fi

  # Build
  echo "   Building..."
  if eval "$BUILD" > /tmp/eos_build_$NAME.log 2>&1; then
    echo "   ✅ Build succeeded"
    ((PASS++))
  else
    echo "   ❌ Build FAILED (see /tmp/eos_build_$NAME.log)"
    ((FAIL++))
  fi

  # Test
  echo "   Testing..."
  if eval "$TEST" > /tmp/eos_test_$NAME.log 2>&1; then
    echo "   ✅ Tests passed"
  else
    echo "   ⚠️  Tests had failures (see /tmp/eos_test_$NAME.log)"
  fi

  cd "$ROOT"
  echo ""

done < <(node -e "
const repos = JSON.parse(require('fs').readFileSync('/tmp/eos_build_list.json','utf8'));
repos.forEach(r => console.log(JSON.stringify(r)));
")

# ── Summary ───────────────────────────────────────────────────────────────────
echo "══════════════════════════════════════════════════════"
echo "  Build Summary"
echo "  ✅ Passed: $PASS"
echo "  ❌ Failed: $FAIL"
echo "  ⏭️  Skipped: $SKIP"
echo "══════════════════════════════════════════════════════"
echo ""

[[ $FAIL -gt 0 ]] && exit 1 || exit 0
