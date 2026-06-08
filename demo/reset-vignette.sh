#!/usr/bin/env bash
# Reset the Layer-2 vignette to a clean state so you can rehearse it repeatedly.
#
# Practice rules this enforces:
#   - Rehearse on a throwaway branch: droid/bug-1/practice (never run-01).
#   - Practice PRs are CLOSED, never merged.
#   - It NEVER touches main, demo/bug-1-base, bug-1-base, or the live issue #13.
#   - Use scratch issue #14 for rehearsal PR links (not #13).
#
# What it does (idempotent):
#   1. Closes any open practice PR (head = practice branch) WITHOUT merging.
#   2. Deletes the practice branch on origin (if present).
#   3. Discards local edits and recreates the practice branch fresh off bug-1-base.
#   4. Purges harness run records whose branch is the practice branch.
#
# Usage:  demo/reset-vignette.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
PY="${REPO_ROOT}/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

BASE="bug-1-base"
PRACTICE="droid/bug-1/practice"
SCRATCH_ISSUE=14

# Safety: refuse to run if the frozen base branch is missing.
if ! git show-ref --verify --quiet "refs/heads/${BASE}"; then
  echo "ERROR: base branch '${BASE}' not found. Aborting (won't improvise)." >&2
  exit 1
fi

# Safety: this script discards tracked edits. Only allow that when we're already
# on the practice branch (discarding the practice fix is intended) OR the tree is
# clean. Otherwise abort so we never clobber unrelated uncommitted work.
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "$PRACTICE" ] && [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "ERROR: uncommitted tracked changes on '$CURRENT_BRANCH'." >&2
  echo "       Commit or stash them first — this script discards tracked edits" >&2
  echo "       and refuses to risk unrelated work. (Safe to run from '$PRACTICE'.)" >&2
  exit 1
fi

echo "== 1/4 close any open practice PR (no merge) =="
if command -v gh >/dev/null 2>&1; then
  for n in $(gh pr list --head "$PRACTICE" --state open --json number -q '.[].number' 2>/dev/null); do
    echo "  closing PR #$n"
    gh pr close "$n" --comment "Closing rehearsal PR (practice run, not merged)." || true
  done
else
  echo "  gh not found; skipping PR close"
fi

echo "== 2/4 delete practice branch on origin (if present) =="
git push origin --delete "$PRACTICE" 2>/dev/null && echo "  deleted origin/$PRACTICE" || echo "  none on origin"

echo "== 3/4 recreate practice branch fresh off $BASE =="
git checkout -- . 2>/dev/null || true        # discard tracked edits on current branch
git switch -C "$PRACTICE" "$BASE"             # reset practice to base and check it out
# Warn (do not auto-delete) if stray untracked product files remain.
STRAY="$(git status --porcelain --untracked-files=all | awk '$1=="??"{print $2}' \
         | grep -vE '^(demo/|AGENTS.md|.factory/)' || true)"
if [ -n "$STRAY" ]; then
  echo "  !! untracked product files present (left in place, review manually):"
  echo "$STRAY" | sed 's/^/     /'
fi

echo "== 4/4 purge practice run records (branch == $PRACTICE) =="
"$PY" - "$PRACTICE" <<'PY'
import json, sys, glob, os
practice = sys.argv[1]
runs_dir = os.path.join("demo", "results", "runs")
cur = os.path.join("demo", "results", ".current")
removed = []
for f in glob.glob(os.path.join(runs_dir, "*.json")):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if d.get("branch") == practice:
        rid = d.get("run_id", "")
        os.remove(f)
        removed.append(rid)
        if os.path.exists(cur) and open(cur).read().strip() == rid:
            os.remove(cur)
print(f"  purged {len(removed)} practice record(s): {', '.join(removed) if removed else '(none)'}")
PY

echo
echo "Ready to rehearse on branch '$PRACTICE' (off $BASE)."
echo "Reminders:"
echo "  - start the clock: demo/measure.py start --arm droid --task bug-1 --branch $PRACTICE"
echo "  - link rehearsal PRs to scratch issue #$SCRATCH_ISSUE (NOT #13)"
echo "  - open the PR but DO NOT merge; re-run this script to reset."
