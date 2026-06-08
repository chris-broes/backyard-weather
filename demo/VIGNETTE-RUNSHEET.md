# Layer-2 vignette — runsheet (the exact steps)

Copy-paste sequence to run the **bug → merged PR, hands-off** flow. Narration cues
live in `TALK-TRACK.md` §4. Conceptual spec in `RUNBOOK.md` §9b.

- **Rehearse with scratch issue #14**, branch `droid/bug-1/practice`, **never merge**.
- **Go live with issue #13**, branch `droid/bug-1/run-01`, `--keyword Fixes`, then merge + close.
- Assets used: `reset-vignette.sh`, `fix-from-issue.sh`, `review-pr.sh`, `risk-app-reviewer` droid.

---

## One-time pre-flight (already done — verify)
```bash
gh auth status                                  # logged in
git ls-remote --heads origin | grep demo/bug-1-base   # PR base exists on origin
gh issue view 14 >/dev/null && echo "scratch issue ok"
```
If `demo/bug-1-base` is missing on origin: `git push origin bug-1-base:demo/bug-1-base`

---

## Rehearsal loop (repeat as many times as you like)

### 0 · Reset to a clean practice branch
```bash
demo/reset-vignette.sh
```
→ leaves you on a fresh `droid/bug-1/practice` off `bug-1-base`, clean tree.

### 1 · [SAY: "a bug report lands"] Show the incident
```bash
gh issue view 14 --web        # or: gh issue view 14
```

### 2 · [SAY: "one trigger"] Headless fix → linked PR
```bash
demo/fix-from-issue.sh --issue 14
```
What it does (watch it happen): starts the clock → `droid exec` reproduces, writes
the regression test green + the fix following `AGENTS.md` → stops clock + collects
metrics → commits only the product fix → pushes → opens a PR (`refs #14`) against
`demo/bug-1-base`. **Note the printed PR number and run id.**

### 3 · [SAY: "well-formed, linked PR"] Show the PR
```bash
gh pr view <PR_NUM> --web
```
Point out: title, summary/test plan, the issue link, the diff is just the fix.

### 4 · [SAY: "governed review in the pipeline"] Review the PR
Run the **`risk-app-reviewer`** droid (interactive `droid` session) on the diff:
> "Review the diff of `droid/bug-1/practice` vs `bug-1-base` using your rubric.
>  Output the findings table and the `REVIEW_SUMMARY` line."

Then post the findings to the PR **and** record them:
```bash
demo/review-pr.sh --pr <PR_NUM> --run <RUN_ID> \
  --summary '{"critical":0,"high":0,"medium":0,"low":1,"nit":0,"total":1}' \
  --findings /tmp/review.md      # paste the reviewer's markdown into this file
```

### 5 · [SAY: "gates"] Show CI (narrate CodeQL)
```bash
gh pr checks <PR_NUM>
```
CI (tests + lint) runs live on every PR. **Narrate:** CodeQL runs on PRs to `main`
only, so it's scoped out here.

### 6 · [SAY: "close the loop"] Narrate closure — DO NOT MERGE in rehearsal
Say: *"On the live run, merging closes the issue and notifies stakeholders."*
(Optional visual: `gh pr comment <PR_NUM> --body "Rehearsal — would merge + close #14."`)

### 7 · Teardown / reset for the next take
```bash
demo/reset-vignette.sh        # closes the practice PR (no merge), deletes the
                              # remote practice branch, purges practice run records
```

---

## Going live (the real take)
Same flow, three changes:
1. Reset is **not** used (you keep the real run). Start clean on the live branch:
   ```bash
   git switch droid/bug-1/run-01 && git status --porcelain   # must be empty
   ```
2. Trigger against the real issue with an auto-link keyword:
   ```bash
   demo/fix-from-issue.sh --issue 13 --keyword Fixes --title "Fix: preserve negative sign in _parse_float"
   ```
3. After review + CI, **merge**, then close the loop:
   ```bash
   gh pr merge <PR_NUM> --squash
   gh issue close 13 --comment "Resolved by the merged PR."   # explicit close (PR base isn't the default branch)
   ```
   > Honesty note: GitHub's keyword auto-close only fires on merges into the
   > **default branch**. Since the PR base is `demo/bug-1-base`, we close the issue
   > explicitly as part of the workflow — same outcome, no surprise on stage.

---

## If something stalls
- `droid exec` pauses for a permission → re-run with `--yolo` (throwaway branch only):
  `demo/fix-from-issue.sh --issue 14 --yolo`
- "working tree not clean" → run `demo/reset-vignette.sh` first.
- Wrong branch → `reset-vignette.sh` always re-bases you onto a clean practice branch.
- Need the run id later → `cat demo/results/.current` or `ls -t demo/results/runs | head`.
