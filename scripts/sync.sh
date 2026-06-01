#!/usr/bin/env bash
# sync.sh — Sync all EoS repos to latest master and update the manifest.
# Usage: bash scripts/sync.sh [--dry-run]
set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

WORKDIR="${EOS_WORKDIR:-$HOME/eos-build}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "🔄 EoS Stack — Sync All Repos"
echo "   Workdir: $WORKDIR"
echo ""

# Update manifest first
echo "── Updating manifest ────────────────────────────────"
if $DRY_RUN; then
  node "$ROOT/scripts/discover.mjs" --dry-run
else
  node "$ROOT/scripts/discover.mjs"
fi
echo ""

# Sync each repo
node -e "
const m = JSON.parse(require('fs').readFileSync('$ROOT/manifest.json','utf8'));
m.projects.filter(p => p.platform !== 'meta').forEach(p => {
  console.log(p.name + '|' + p.repo + '|' + p.defaultBranch);
});
" | while IFS='|' read -r NAME REPO BRANCH; do
  REPO_DIR="$WORKDIR/$NAME"
  echo "── $NAME"
  if $DRY_RUN; then
    echo "   [DRY RUN] Would sync $REPO → $REPO_DIR"
    continue
  fi
  if [[ -d "$REPO_DIR/.git" ]]; then
    git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
    git -C "$REPO_DIR" reset --hard "origin/$BRANCH" --quiet
    echo "   ✅ Synced to origin/$BRANCH"
  else
    git clone --depth=1 -b "$BRANCH" "https://github.com/$REPO.git" "$REPO_DIR" --quiet
    echo "   ✅ Cloned $REPO"
  fi
done

echo ""
echo "✅ Sync complete"
echo ""
