# Measurement harness — operating guide

Two arms (`baseline` vs `droid`), many samples each. Run as many paired samples
as you need; `aggregate` computes per-arm statistics + a head-to-head verdict so
the hypothesis (Droid faster / more complete) is validated across runs, not
anecdotally. All commands use the project venv.

## Interactive shell (avoids retyping the python path)
```bash
.venv/bin/python demo/measure.py shell    # or just `.venv/bin/python demo/measure.py`
```
Then type bare commands (`start --arm droid --task task-b`, `stop`,
`collect --skip-audit`, `aggregate --task task-b`). The prompt shows the current
run + branch, e.g. `measure[droid_task-b_01 @droid/task-b/run-01]>`. It defaults
`SECRET_KEY=demo` for the session; `help` lists commands, `exit`/Ctrl-D leaves.
All the one-shot commands below work identically inside the shell (drop the
`.venv/bin/python demo/measure.py` prefix).

## Setup (once)
```bash
.venv/bin/python -m pip install -r requirements-dev.txt
git tag demo-base 091d8a4              # frozen starting point for every run
export SECRET_KEY=demo                 # app refuses to boot without it
.venv/bin/python demo/measure.py snapshot-base   # records base tests/coverage for deltas
```

## Per-run lifecycle (repeat for each sample, both arms)
```bash
# 1. branch off the frozen base
git switch demo-base && git switch -c droid/task-a/run-01

# 2. start the clock (arm = baseline|droid, task = task-a|task-b)
.venv/bin/python demo/measure.py start --arm droid --task task-a

# 3. do the work (Droid session, or Copilot for the baseline arm)
#    log each human intervention as it happens:
.venv/bin/python demo/measure.py turn

# 4. stop when the Definition of Done is met
.venv/bin/python demo/measure.py stop

# 5. auto-collect quality / security / DoD metrics
.venv/bin/python demo/measure.py collect --skip-audit
#    add --ci-branch <branch> to pull GitHub Actions "time-to-green" via gh
#    drop --skip-audit to include pip-audit (needs network)
```

## Capturing CI / CodeQL / PR quality (optional, after the run)
These need the run branch pushed and a PR opened so GitHub Actions + CodeQL run.
Do it *after* `collect` so it never re-runs pytest or clobbers local metrics:
```bash
git push -u origin droid/task-a/run-01
gh pr create --base main --head droid/task-a/run-01 --fill
# wait for Actions + CodeQL to finish, then:
.venv/bin/python demo/measure.py ci --run droid_task-a_01
```
`ci` backfills: CI conclusion + time-to-green, open CodeQL alert counts, and PR
diff size / check rollup. (On an un-analyzed branch CodeQL returns 0 = "no data
yet", not "clean" — only trust it once CodeQL has actually run on the PR.)

## Compare
```bash
.venv/bin/python demo/measure.py aggregate --task task-a   # writes demo/results/summary_task-a.md
.venv/bin/python demo/measure.py aggregate                 # all tasks combined
```
Includes **throughput** (`tests_per_min`, `coverage_per_min`) — quality-adjusted
speed, which de-confounds raw time-to-done when one agent simply does more work.

## What is captured

| Tier | Metrics | How |
|---|---|---|
| Auto (objective) | tests_total, tests_added, coverage %, coverage Δ, flake8, bandit, pip-audit, **DoD completeness**, CI time-to-green | `collect` runs the tools; `gh` for CI |
| Semi (operator-triggered) | duration (time-to-done) | `start` / `stop` timestamps |
| Manual (logged) | human_turns | `turn` increments a counter |

- **Lead metric:** `duration_sec` (time-to-done) → lead time for changes.
- DoD is graded by `demo/dod/check_task_a.py` / `check_task_b.py` (full/partial/none).
- Results live in `demo/results/runs/*.json`; base reference in `.base_metrics.json`.

## Baseline (pre-recorded column)
Run the baseline arm before the demo with the *exact same* task spec, using the
same lifecycle above with `--arm baseline`. Save screenshots/diffs under
`demo/baseline/`. Frozen specs + shared harness = the only variable is the tool.
