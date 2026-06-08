#!/usr/bin/env bash
# Layer-2 vignette, star beat: one trigger -> Droid fixes a GitHub issue headlessly
# (via `droid exec`), following AGENTS.md, then opens a linked PR.
#
# Runs on the CURRENT branch (must be clean) — pair it with reset-vignette.sh,
# which checks out a fresh practice branch off bug-1-base.
#
# REHEARSAL (default): links the scratch issue with "refs" (no auto-close), PR base
#   = demo/bug-1-base. LIVE: pass --issue 13 --keyword Fixes.
#
# Usage:
#   demo/reset-vignette.sh                 # clean practice branch first
#   demo/fix-from-issue.sh --issue 14      # rehearsal
#   demo/fix-from-issue.sh --issue 13 --keyword Fixes --title "Fix negative-number parsing"
#
# Options:
#   --issue N        GitHub issue number (required)
#   --target BR      PR base branch on origin (default: demo/bug-1-base)
#   --keyword W      issue link keyword: refs|Fixes|Closes (default: refs)
#   --title S        PR title (default derived)
#   --model ID       model for droid exec (default: claude-opus-4-8)
#   --auto LEVEL     droid autonomy: low|medium|high (default: high)
#   --yolo           add --skip-permissions-unsafe (only on a throwaway branch)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
PY="${REPO_ROOT}/.venv/bin/python"; [ -x "$PY" ] || PY="python3"

ISSUE="" ; TARGET="demo/bug-1-base" ; KEYWORD="refs" ; TITLE="" ; MODEL="claude-opus-4-8" ; AUTO="high" ; YOLO=""
while [ $# -gt 0 ]; do case "$1" in
  --issue) ISSUE="$2"; shift 2;;
  --target) TARGET="$2"; shift 2;;
  --keyword) KEYWORD="$2"; shift 2;;
  --title) TITLE="$2"; shift 2;;
  --model) MODEL="$2"; shift 2;;
  --auto) AUTO="$2"; shift 2;;
  --yolo) YOLO="1"; shift;;
  *) echo "unknown arg: $1" >&2; exit 2;;
esac; done

[ -n "$ISSUE" ] || { echo "usage: demo/fix-from-issue.sh --issue N [--keyword Fixes] [--target BR]" >&2; exit 2; }
HEAD_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ -z "$TITLE" ] && TITLE="fix: resolve issue #${ISSUE}"

# --- Gate: clean tree so the fix PR contains ONLY the fix ---
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: working tree not clean. Run demo/reset-vignette.sh first." >&2
  git status --short >&2; exit 1
fi
echo "Branch: $HEAD_BRANCH   Issue: #$ISSUE   PR base: $TARGET   Link: '$KEYWORD #$ISSUE'"

# --- Pull the issue (source of truth) ---
ISSUE_BODY="$(gh issue view "$ISSUE" --json title,body -q '"# " + .title + "\n\n" + .body')"

# --- Build the headless prompt (enforces AGENTS.md scope/standards) ---
PROMPT_FILE="$(mktemp)"
cat > "$PROMPT_FILE" <<EOF
Fix the bug reported in GitHub issue #${ISSUE}:

${ISSUE_BODY}

Requirements:
- Find and fix the ROOT CAUSE in the application code (not the test).
- A regression test exists at tests/test_regression_bug1.py and is currently
  FAILING; make it pass (add cases only if needed).
- Follow the conventions and Definition of Done in AGENTS.md (units, SSRF hygiene,
  no debug mode, type hints, tests required).
- Keep it a single, minimal, reviewable change.
- Do NOT modify anything under demo/ or .factory/.
- Ensure \`python -m pytest -q\` passes and \`flake8 . --max-line-length=127\` does not regress.
- Do NOT commit, push, or open a PR — only make the code changes.
EOF

# --- Start clock, run Droid headless, stop clock, collect metrics ---
"$PY" demo/measure.py start --arm droid --task bug-1 --branch "$HEAD_BRANCH" --model "$MODEL"
RUN_ID="$(cat demo/results/.current 2>/dev/null || true)"   # capture before stop clears it
if [ -n "$YOLO" ]; then PERM_FLAGS="--skip-permissions-unsafe"; else PERM_FLAGS="--auto $AUTO"; fi
echo ">> droid exec ($PERM_FLAGS, model=$MODEL) ..."
SECRET_KEY=demo droid exec -f "$PROMPT_FILE" $PERM_FLAGS -m "$MODEL" --cwd "$REPO_ROOT"
rm -f "$PROMPT_FILE"
"$PY" demo/measure.py stop --run "$RUN_ID"
"$PY" demo/measure.py collect --run "$RUN_ID" --skip-audit

# --- Commit ONLY the product fix (never demo/.factory tooling) ---
git add -A && git reset -q -- demo .factory 2>/dev/null || true
if git diff --cached --quiet; then
  echo "ERROR: Droid produced no committable change. Aborting before PR." >&2; exit 1
fi
git commit -q -m "droid: fix issue #${ISSUE} (headless via droid exec)"
echo "Committed fix:"; git show --stat --oneline HEAD | head -8

# --- Push + open the linked PR ---
git push -u origin "$HEAD_BRANCH"
PR_BODY="${KEYWORD} #${ISSUE}

Resolves the bug in #${ISSUE}. Regression test: tests/test_regression_bug1.py.
Generated headlessly by \`droid exec\` following AGENTS.md."
PR_URL="$(gh pr create --base "$TARGET" --head "$HEAD_BRANCH" --title "$TITLE" --body "$PR_BODY")"

echo
echo "PR opened: $PR_URL"
echo "Run record: ${RUN_ID:-<see demo/results/runs>}"
echo
echo "Next beats:"
echo "  - Review (interactive risk-app-reviewer on the diff) then:"
echo "      demo/review-pr.sh --pr <num> --run ${RUN_ID:-<run-id>} --summary '<REVIEW_SUMMARY json>' --findings <file>"
echo "  - Show CI:   gh pr checks <num>"
echo "  - Reset:     demo/reset-vignette.sh   (closes the practice PR, no merge)"
