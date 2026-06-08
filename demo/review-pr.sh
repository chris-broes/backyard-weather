#!/usr/bin/env bash
# Post the neutral review-droid's findings to a PR AND record them in the
# scorecard. Bridges `.factory/droids/risk-app-reviewer.md` output ->
# GitHub PR comment + `demo/measure.py review`.
#
# Usage:
#   demo/review-pr.sh --pr <number|branch> --run <run-id> \
#                     --summary '{"critical":0,"high":0,"medium":1,"low":3,"nit":1,"total":5}' \
#                     [--findings <markdown-file>]
#
# Example:
#   demo/review-pr.sh --pr 7 --run droid_bug-1_01 \
#       --summary '{"critical":0,"high":0,"medium":0,"low":1,"nit":0,"total":1}' \
#       --findings /tmp/review_A.md
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${REPO_ROOT}/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

PR="" ; RUN="" ; SUMMARY="" ; FINDINGS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --pr) PR="$2"; shift 2;;
    --run) RUN="$2"; shift 2;;
    --summary) SUMMARY="$2"; shift 2;;
    --findings) FINDINGS="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

if [ -z "$PR" ] || [ -z "$RUN" ] || [ -z "$SUMMARY" ]; then
  echo "usage: demo/review-pr.sh --pr <num|branch> --run <run-id> --summary '<json>' [--findings <file>]" >&2
  exit 2
fi

# 1) Post the review to the PR as a governance artifact.
BODY_FILE="$(mktemp)"
{
  echo "## Automated review — \`risk-app-reviewer\` droid"
  echo
  if [ -n "$FINDINGS" ] && [ -f "$FINDINGS" ]; then
    cat "$FINDINGS"
    echo
  fi
  echo '```'
  echo "REVIEW_SUMMARY ${SUMMARY}"
  echo '```'
  echo
  echo "_Neutral referee, same rubric both arms. Recorded to the demo scorecard (run \`${RUN}\`)._"
} > "$BODY_FILE"

echo "Posting review comment to PR ${PR} ..."
gh pr comment "$PR" --body-file "$BODY_FILE"
rm -f "$BODY_FILE"

# 2) Record into the scorecard.
echo "Recording review into scorecard for run ${RUN} ..."
"$PY" "${REPO_ROOT}/demo/measure.py" review --run "$RUN" --json "$SUMMARY"

echo "Done."
