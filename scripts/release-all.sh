#!/usr/bin/env bash
# release-all.sh — Tag and trigger releases for all EoS repos.
# Usage: bash scripts/release-all.sh v1.0.0 [--dry-run]
set -euo pipefail

TAG="${1:-}"
DRY_RUN=false
[[ "${2:-}" == "--dry-run" ]] && DRY_RUN=true

if [[ -z "$TAG" ]]; then
  echo "Usage: bash scripts/release-all.sh v1.0.0 [--dry-run]"
  exit 1
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "❌ GH_TOKEN environment variable is required"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "🚀 EoS Stack — Release All"
echo "   Tag: $TAG"
echo "   Dry run: $DRY_RUN"
echo ""

PASS=0
FAIL=0

node -e "
const m = JSON.parse(require('fs').readFileSync('$ROOT/manifest.json','utf8'));
m.projects.filter(p => p.platform !== 'meta' && p.releaseTarget.length > 0).forEach(p => {
  console.log(p.name + '|' + p.repo);
});
" | while IFS='|' read -r NAME REPO; do
  echo "── $NAME ($REPO)"

  if $DRY_RUN; then
    echo "   [DRY RUN] Would create tag $TAG on $REPO"
    ((PASS++))
    continue
  fi

  # Check if tag already exists
  EXISTS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GH_TOKEN" \
    "https://api.github.com/repos/$REPO/git/refs/tags/$TAG")

  if [[ "$EXISTS" == "200" ]]; then
    echo "   ⏭️  Tag $TAG already exists — skipping"
    ((PASS++))
    continue
  fi

  # Get master SHA
  SHA=$(curl -s \
    -H "Authorization: token $GH_TOKEN" \
    "https://api.github.com/repos/$REPO/git/refs/heads/master" \
    | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); process.stdout.write(d.object?.sha||'')")

  if [[ -z "$SHA" ]]; then
    echo "   ❌ Could not get master SHA for $REPO"
    ((FAIL++))
    continue
  fi

  # Create tag
  HTTP=$(curl -s -o /tmp/tag_response.json -w "%{http_code}" \
    -X POST \
    -H "Authorization: token $GH_TOKEN" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$REPO/git/refs" \
    -d "{\"ref\":\"refs/tags/$TAG\",\"sha\":\"$SHA\"}")

  if [[ "$HTTP" == "201" ]]; then
    echo "   ✅ Tagged $REPO@$SHA as $TAG"
    ((PASS++))
  else
    echo "   ❌ Failed to tag $REPO (HTTP $HTTP)"
    cat /tmp/tag_response.json | head -3
    ((FAIL++))
  fi
done

echo ""
echo "══════════════════════════════════════════════════════"
echo "  Release Summary for $TAG"
echo "  ✅ Tagged: $PASS"
echo "  ❌ Failed: $FAIL"
echo "══════════════════════════════════════════════════════"
echo ""

[[ $FAIL -gt 0 ]] && exit 1 || exit 0
