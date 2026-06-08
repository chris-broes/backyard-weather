# Head-to-head development program — Droid vs Copilot
### Phased build-out of the insurance weather risk-scoring product

This program runs the same multi-phase roadmap on **two parallel tracks** — one
built with Factory Droid, one with GitHub Copilot — and measures each phase with
the harness (`demo/measure.py`, see `demo/MEASURE.md`). It produces a stream of
real commits/PRs per arm plus a per-phase and cumulative scorecard.

## Hypothesis
1. **Completeness/quality:** Droid produces more production-ready output (tests,
   coverage, fewer findings) at comparable or better throughput.
2. **Compounding advantage:** Droid's lead *grows* as the codebase matures —
   where managing context and cross-file change separates agents from
   autocomplete. The per-phase trend is the headline visual.

## Execution model — Model B (parallel tracks)
- Two long-lived track branches, each seeded from its Phase-1 result:
  - `track-baseline` (from `baseline/task-a/run-01` → … )
  - `track-droid` (from `droid/task-a/run-01` → … )
- Each phase is a feature branch off the arm's track tip:
  `git switch -c <arm>/<phase-id> track-<arm>`
- Caveat we own openly: later phases are not strict A/B (each arm builds on its
  own prior code). We therefore report **per-phase metrics + cumulative trends**,
  and reserve the **seeded bug** as a strict A/B task (identical start).

### Fairness controls (held constant across both arms)
- **Same underlying model: Claude Opus 4.8** on both the baseline (Copilot) arm
  and the Droid arm — so measured differences are attributable to the
  tool/agent scaffolding, not the LLM.
- Identical frozen prompts (`PROMPTS.md`), identical executable DoD (`dod/`),
  identical starting commit per phase, and one neutral reviewer rubric for both.

## Phase registry

| Phase id | Feature | SDLC type | Factory area showcased | Grader |
|---|---|---|---|---|
| `task-a` | Risk-scoring core ✅ | greenfield feature | productivity (headline) | check_task_a |
| `task-b` | NWS JSON API migration | migration | migration | check_task_b |
| `p2-multiloc` | Multi-location portfolio | feature + data model | productivity | check_p2_multiloc |
| `p3-alerts` | Severe-weather alerts integration | integration | productivity | check_p3_alerts |
| `p4-riskmodel` | Configurable risk model + factors | refactor | productivity / maintainability | check_p4_riskmodel |
| `p5-api` | Insurer REST API + API-key auth | feature + security | productivity + security | check_p5_api |
| `p6-tenant` | Multi-tenant accounts & isolation | security feature | security | check_p6_tenant |
| `p7-postgres` | SQLite → Postgres + migrations | infra migration | migration | check_p7_postgres |
| `p8-security` | Security hardening pass | security workflow | security | check_p8_security |
| `p9-bulk` | Bulk CSV scoring + report export | feature + data | productivity | check_p9_bulk |
| `bug-1` | Seeded-bug triage & fix | support workflow | support / debugging | check_bug_1 |

This single product touches **every** assignment area: feature delivery
(headline), migration, security, support/triage, testing, and DX.

## Sample plan
- **Breadth:** 1 paired sample (baseline + droid) for every phase.
- **Depth:** pick **one headline phase** (recommend `p2-multiloc` or `p5-api` —
  meaty, cross-file) and run **3–5 paired samples** for statistical weight.
- `bug-1`: 3 paired samples (cheap, strict A/B, great support-workflow story).

## Frozen Definition of Done (the contract — identical text to both arms)

> Phase 0 (`task-a`) and Phase 1 (`task-b`) DoDs live in `RUNBOOK.md` §7.

**p2-multiloc — Multi-location portfolio**
- `Location` model (name + lat/lon or NWS zone/station); add & list locations.
- Weather fetch parameterized by location (no hardcoded SF lat/lon/station).
- Risk score computed and shown per location.
- Tests cover multiple locations. Suite green, flake8 clean, no new findings.

**p3-alerts — Severe-weather alerts integration**
- Fetch active alerts from `api.weather.gov/alerts` for a location.
- Active alerts factor into the risk score (documented contribution).
- Alerts surfaced in the UI; event fields (event/severity/expiry) parsed.
- Fixture-based tests (no live network). Suite green, clean.

**p4-riskmodel — Configurable risk model + factors**
- Weights and bands externalized to config (not inline literals).
- At least one new factor (e.g. precipitation/gust/alert) added.
- Model carries a version constant; existing behavior covered by tests.
- Tests for new factors + config loading. Suite green, clean.

**p5-api — Insurer REST API + API-key auth**
- Versioned JSON endpoints under `/api/v1/...` returning risk data.
- API-key auth (header), 401 on missing/invalid key.
- Basic rate limiting.
- API tests (authorized + unauthorized). Suite green, clean.

**p6-tenant — Multi-tenant accounts & isolation**
- `User`/`Account` model with hashed passwords; login.
- Data scoped per account (FK); data routes require auth.
- Isolation test: one account cannot read another's data.
- Suite green, clean.

**p7-postgres — SQLite → Postgres + migrations**
- App boots against Postgres via `DATABASE_URL`; `psycopg` in requirements.
- Alembic migration(s) for current schema; documented run steps.
- Suite green (sqlite acceptable in CI). *Manual/CI check: boots on Postgres.*

**p8-security — Security hardening pass**
- SSRF guard (host allowlist) on outbound weather fetches.
- Security headers; CSRF on; input validation on user-supplied data.
- bandit: **0 medium/high**; CodeQL: **0 open alerts**; deps audited.
- Security regression tests. *(Primary signal: bandit_total + codeql_alerts.)*

**p9-bulk — Bulk CSV scoring + report export**
- Upload endpoint scoring a portfolio CSV; validates input (`secure_filename`).
- Export results as CSV (and/or PDF) with proper download headers.
- Tests with a sample CSV. Suite green, clean.

**bug-1 — Seeded-bug triage & fix (support workflow)**
- *Seed first* (identical for both arms): introduce a realistic defect plus a
  failing regression test, e.g. `tests/test_regression_bug1.py`. Suggested seed:
  break wind-direction normalization (return raw text instead of compass code)
  or a pressure unit mismatch, with a test asserting the correct output.
- DoD: root cause fixed, `test_regression_bug1.py` passes, full suite green, no
  scope creep.

## Per-sample checklist (run for each phase, each arm)

```bash
export SECRET_KEY=demo
ARM=droid           # or baseline
PHASE=p2-multiloc

# 1. branch off the arm's track tip (use demo-base only for the very first phase)
git switch -c $ARM/$PHASE track-$ARM

# 2. start clock, then hand the frozen DoD to the agent
.venv/bin/python demo/measure.py start --arm $ARM --task $PHASE
#    ... agent works ... log substantive interventions:
.venv/bin/python demo/measure.py turn

# 3. stop + local metrics
.venv/bin/python demo/measure.py stop
.venv/bin/python demo/measure.py collect --skip-audit

# 4. confirm green, then merge into the track so the next phase builds on it
.venv/bin/python -m pytest -q
git commit -am "$ARM $PHASE"
git switch track-$ARM && git merge --no-ff $ARM/$PHASE

# 5. (optional, for CI/CodeQL/PR data) push + open a PR to main to fire the
#    workflows, wait for them, backfill, then close the PR without merging
git push -u origin $ARM/$PHASE
gh pr create --base main --head $ARM/$PHASE --fill --draft
#    ... wait for Actions + CodeQL ...
.venv/bin/python demo/measure.py ci --run ${ARM}_${PHASE}_01
```

> Note: `codeql.yml` triggers on PRs to `main`, so PR each phase branch to `main`
> (draft, don't merge) to capture CodeQL. `python-app.yml` runs on every push/PR.

## Reading the results
- Per phase: `aggregate --task <phase>` → time, throughput, coverage, findings,
  CI time-to-green, CodeQL alerts, PR diff size.
- Across phases: track each arm's per-phase numbers to show the **compounding
  curve** (does Droid's margin widen as complexity grows?).
- `bug-1`: strict A/B — time-to-fix + suite-green is the support-workflow proof.

## Limitations (state them)
Single repo; small N on most phases; one operator; parallel tracks diverge by
design. The harness is reproducible — the argument is the *workflow and trend*,
not the absolute numbers.
