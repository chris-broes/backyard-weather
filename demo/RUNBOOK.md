# Factory Droid Demo Runbook
### `python_weather` — Insurance Weather Risk Scoring

> **Audience:** technical buyer (eng leader / staff engineer) on a live screen-share.
> **Headline:** Engineering productivity / feature delivery.
> **Supporting acts:** Migration / modernization, and a light touch of Developer Experience.
> **Primary success metric:** Speed — time-to-mergeable-PR (lead time for changes).

---

## 1. The one-liner

> "Your product's *core differentiator* — the weather risk score — is unfinished and unwired.
> Watch Factory Droid take it from a dead stub to a tested, secured, production-grade feature in one
> session, then modernize the data pipeline behind it — and we'll measure exactly how much faster
> that is than your current AI-assisted workflow."

---

## 2. Why this repo is the perfect stage

`python_weather` is a Flask app meant to give insurers a **risk score** from user-reported and
weather-station data. In reality:

- **The differentiator is a stub.** `risk-scoring.py` is *orphaned*: never imported, hyphenated
  filename can't even be imported as a module, no route, no UI, no tests. The business value the
  product promises does not exist in the running app.
- **The data pipeline is brittle.** Current conditions are scraped from weather.gov HTML with
  BeautifulSoup across two fragile selectors — exactly the kind of thing that silently breaks.
- **The SDLC scaffolding is real but theatrical.** CI runs flake8 + pytest and then a literal
  `echo "Running security checks..."` placeholder. There's a separate CodeQL workflow, a past
  CodeQL finding (Flask debug mode), and git history showing a committed-then-removed `.env` secret.

That gives us an honest, relatable starting point: a half-built product with believable tech debt.

---

## 3. Narrative arc

```
ACT 0  The problem        →  show the stub + brittle pipeline (2 min)
ACT 1  HEADLINE            →  Droid finishes the risk-scoring feature, live (8-10 min)
ACT 2  SUPPORTING          →  Droid migrates scraping → official NWS JSON API (5-6 min)
ACT 3  DX (light)          →  AGENTS.md + custom review droid in action (3 min)
ACT 4  MEASURE             →  the bake-off scorecard, speed headline (4 min)
ACT 5  BUSINESS ROLL-UP    →  map task-level wins to DORA / SPACE language (2 min)
```

Total live time ≈ 25–27 min, leaving room for Q&A.

---

## 4. Pre-demo setup checklist

Do all of this **before** the call so the live portion is clean.

- [ ] Clean working tree on a known commit; create demo branch from it: `git switch -c demo/live`.
- [ ] `.venv` active; `pip install -r requirements.txt` succeeds; `pytest` is green.
- [ ] `SECRET_KEY` exported (app refuses to boot without it) and app runs at `127.0.0.1:5000`.
- [ ] **Baseline column captured** (see §6) and saved under `demo/baseline/` — screenshots,
      timings, and the resulting diff/PR from the Copilot (or manual) run.
- [ ] Scorecard script runs locally and prints a clean table (see §8).
- [ ] Two browser tabs ready: the running app, and the GitHub repo PR view.
- [ ] Droid session open in the repo with `AGENTS.md` present and the custom review droid installed.
- [ ] Rollback safety: tag the pre-demo commit so you can reset instantly between dry runs.

---

## 5. Minute-by-minute script (talk track + actions)

### ACT 0 — The problem (2 min)
- **Say:** "This app sells insurers a weather risk score. Let's look at where that score lives."
- **Do:** Open `risk-scoring.py`. Point out it's never imported, the filename can't be imported,
  no tests, no endpoint. Open the app — there's no risk score anywhere in the UI.
- **Say:** "So the headline capability is vaporware today. This is the kind of half-finished work
  every backlog has. Let's close it — and time it."

### ACT 1 — HEADLINE: feature delivery (8–10 min)
- **Do:** In Droid, hand it **Task A** (frozen spec, §7). Let it run spec → plan → implement.
- **Narrate while it works:**
  - It renames/relocates the module so it's importable, integrates the scoring into the data model
    and a real endpoint, surfaces the score in the UI, and **adds tests + edge-case handling**.
  - Call out that it reads `AGENTS.md` for conventions (DX hook) and respects the existing CI gates.
- **Do:** Run `pytest` live — green. Show the risk score now rendered in the app.
- **Say:** "From dead stub to tested feature, end to end, with no babysitting. Mark the clock."

### ACT 2 — SUPPORTING: migration (5–6 min)
- **Say:** "The score is only as good as the data. Today it's screen-scraped HTML — fragile."
- **Do:** Hand Droid **Task B** (§7): migrate scraping → the official NWS JSON API
  (`api.weather.gov`) behind a clean provider abstraction, keeping the parser path as fallback,
  with tests using recorded fixtures.
- **Narrate:** legacy-to-modern migration with behavior parity proven by tests, not vibes.
- **Do:** Run `pytest` — still green.

### ACT 3 — DX, light touch (3 min)
- **Do:** Show `AGENTS.md` (migrated from `.github/copilot-instructions.md`) and explain how Droid
  used it for conventions and commands.
- **Do:** Trigger the **custom review droid** on the open PR; show it flag/triage issues
  (e.g., the fake security step, debug-mode risk, secret-handling hygiene).
- **Say:** "Same context, codified once, reused by every agent and every teammate."

### ACT 4 — MEASURE: the bake-off (4 min)
- **Do:** Open the **scorecard** side-by-side: pre-recorded baseline column vs the Droid run you
  just did. Lead with **time-to-mergeable-PR**.
- **Show the table** (§8): speed, autonomy (human turns), completeness, quality/coverage, security
  findings, and human-minutes saved.
- **Say:** "Speed is the headline, but notice the quality gates were enforced the whole time, so the
  fast path is also the safe path."

### ACT 5 — BUSINESS ROLL-UP (2 min)
- **Say:** "Task-level wins compound into the metrics you already track:"
  - Faster time-to-PR → **shorter lead time for changes** (DORA).
  - Tests + security gates enforced by default → **lower change failure rate** (DORA).
  - Less human attention per task → **throughput + developer satisfaction** (SPACE).
- **Close:** "We measured one feature and one migration. Multiply across your backlog."

---

## 6. Measurement model

### Two layers
1. **Live / concrete — task-level bake-off.** Identical frozen tasks, identical starting commit,
   identical definition-of-done, identical reviewer, and the **same underlying model on both arms
   (Claude Opus 4.8)** — so deltas reflect the tool/agent, not the LLM. Objective deltas only.
2. **Framing — business roll-up.** Translate task-level results into DORA / SPACE language the buyer
   already tracks. DORA is *not* measured live (it's longitudinal and confounded); it's the
   vocabulary for the closing slide.

### Why not "show a DORA delta live"
DORA's four keys need weeks of history and are influenced by many variables. Presenting a
Droid-attributable DORA delta from a 25-minute demo would not survive a technical buyer's scrutiny.
We earn credibility by measuring what's honestly measurable (task time + quality) and *mapping* it.

### Baseline capture protocol (pre-recorded column)
Capture the baseline arm **before** the call, using the same task specs:
1. Reset repo to the frozen starting commit.
2. Run the task using the baseline tool (Copilot in VS Code, or a manual no-agent run).
3. Record: start timestamp, end timestamp (first green, mergeable diff), number of human
   prompts/interventions, whether the DoD was fully met, and the resulting diff.
4. Run the scorecard script against the baseline branch; save output + screenshots to
   `demo/baseline/`.
5. Note honest limitations (single repo, N=1, operator familiarity) on the scorecard.

### Primary metric (weighted highest): **Speed**
Time-to-mergeable-PR = first commit on the task branch → branch is green on all CI gates and meets
DoD. Reported in minutes. This is the number we lead with.

---

## 7. Frozen task specs (Definition of Done)

> These are fixed contracts. Both arms (baseline and Droid) get the *exact same* text. No edits
> mid-demo. This is what makes the comparison fair.

### Task A — Finish the risk-scoring capability (HEADLINE)
**Goal:** Turn the orphaned scorer into a real, tested, surfaced product capability.

**Done when:**
- Scoring logic lives in an importable module (no hyphen) with type hints and docstrings.
- Inputs are validated; out-of-range / missing values are handled explicitly (no crashes).
- A risk score (and a human-readable band, e.g. Low/Moderate/High) is computed for each weather
  entry and **surfaced in the UI** and via a JSON endpoint (e.g. `GET /risk` or per-entry field).
- Unit tests cover the scoring bands and edge cases; functional test asserts the score renders.
- `pytest` green, flake8 clean, no new security findings.
- A single, reviewable PR with a clear description.

### Task B — Migrate the weather data pipeline (SUPPORTING)
**Goal:** Replace brittle HTML scraping with the official NWS JSON API.

**Done when:**
- A provider abstraction fetches current conditions from `api.weather.gov` (JSON), with the
  HTML-scrape path retained as a documented fallback.
- Units/fields normalized to the existing model (°F, inHg, mph, direction, % humidity).
- Tests use recorded fixtures (no live network in CI); behavior parity demonstrated.
- `pytest` green, flake8 clean, no new security findings.
- A single, reviewable PR with a clear description.

---

## 8. Scorecard definition

A `demo/scorecard.py` (built after runbook approval) computes objective metrics from a task branch
and prints a comparison table. Columns: **Baseline** vs **Droid**.

| Metric | Source | Notes |
|---|---|---|
| **Time-to-mergeable-PR (min)** ⭐ | git timestamps + CI status | Primary, weighted highest |
| Human turns / interventions | manual log | Proxy for attention cost |
| DoD completeness (full/partial/none) | manual vs §7 | Reliability |
| Tests added / total | pytest collection diff | Quality |
| Coverage % delta | `pytest --cov` | Quality |
| Lint findings | flake8 | Quality gate |
| Security findings (new vs fixed) | bandit / pip-audit / CodeQL | Risk posture |
| Human-minutes saved | baseline time − droid time (active human time) | ROI |
| Est. $ per task | minutes × loaded rate (+ token cost) | CFO-facing |

⭐ = lead metric for this demo.

Output is a single table the buyer can read at a glance, plus an honest "limitations" footer.

---

## 9. Objection handling (technical-buyer Q&A prep)

- **"N=1 isn't proof."** Agreed — this is a *directional* demo on one repo. The harness is
  reproducible; run it on your own repo and tasks. The point is the workflow, not the sample size.
- **"The baseline operator might be slow / unfamiliar."** That's why specs are frozen and the
  baseline is captured transparently with its diff and prompts shown. Re-run it yourself.
- **"Did it just write code that passes tests it also wrote?"** Tests are part of the DoD and are
  reviewable; the custom review droid and CI gates are independent checks; CodeQL runs on the PR.
- **"How is this different from Copilot autocomplete?"** Copilot accelerates keystrokes; Droid
  executes whole tasks end-to-end (spec → code → tests → PR) with repo context from `AGENTS.md`.
  The scorecard shows the autonomy delta, not just speed.
- **"What about security / our code leaving the building?"** (Have your standard data-handling and
  deployment-model answer ready; point to the enforced gates as a feature, not a bypass.)

---

## 9b. Layer-2 platform vignette — incident → reviewed PR (tied to bug-1)

**Purpose.** The bug-1 head-to-head proves *Layer 1* (better fix at equal model).
This vignette proves *Layer 2* — the **platform workflow** a single terminal
agent (Claude Code / Copilot) doesn't run. Same incident, bigger surface.

**Framing.** On-call gets a data-quality alert: *negative temperatures are being
stored as positive*. A terminal agent fixes the one line you point it at.
Factory runs the whole incident.

**Beats (~4–6 min) and the capability each proves:**

| # | Beat | Layer-2 capability | Executable | Assets |
|---|---|---|---|---|
| 1 | Open the **GitHub Issue** (the bug-1 ticket) as source of truth | Integration / ticket loop | ✅ `gh` | [issue #13](https://github.com/chris-broes/backyard-weather/issues/13) |
| 2 | **Dispatch a fleet in parallel** — Droid A: fix + regression test; Droid B: **sibling-defect sweep** for the same fragility class | Fleet / parallel / async | ✅ | `sibling-sweep` droid |
| 3 | Droid A opens a **PR linked to the issue** (`Fixes #13`) | Ticket → PR action loop | ✅ `gh pr create` | — |
| 4 | **`risk-app-reviewer` droid** reviews the PR; `demo/review-pr.sh` posts findings as a PR comment **and** records them in the scorecard | Reproducible specialist droid, unattended, in-pipeline | ✅ | reviewer droid + helper |
| 5 | CI + CodeQL gate the PR; on merge the **issue auto-closes** | Governance + action loop | ✅ (push/Actions) | CI workflows |

**Why it's the elegant tie-in.** bug-1 is a *parsing-robustness* defect, and the
neutral reviewer already found sibling-class bugs (baseline's `barometricPressure`
present-but-`null` fallback; the wind-unit default). So Droid B's sweep surfaces
**real** issues — the "siblings found" count is a proactive-quality metric the
single-bug fixer never produces.

**Contrast line for the room:** *"Claude Code fixed the one bug you pointed it at.
Factory turned the report into a linked PR, a parallel sibling-defect sweep, an
automated governed review, and a closed ticket — reproducibly, unattended, across
surfaces."*

**Ticket source.** Demo uses **GitHub Issues** (executable today). The enterprise
swap is **Jira / Linear** via Factory's integrations — same loop, the buyer's own
tracker; narrate this unless their integration is configured.

**Honesty guardrails.** Model held constant (Opus 4.8) — this is about the
*workflow*, not the LLM or per-line code quality. The sweep must surface real
defects (it does). Claim the workflow a terminal agent doesn't run; don't
overclaim per-line superiority.

**Execution depth: TBD** (decide live vs narrated for CI/CodeQL + governance closer to demo day).

**Assets created for this vignette:**
- GitHub Issue [#13](https://github.com/chris-broes/backyard-weather/issues/13) (bug-1 ticket) — the incident.
- `.factory/droids/sibling-sweep.md` — read-only specialist that hunts same-class defects.
- `demo/review-pr.sh` — posts the reviewer droid's findings to the PR and into the scorecard.

---

## 10. Build backlog (created after you approve this runbook)

1. `demo/scorecard.py` + results template (speed-weighted).
2. Frozen task spec files for Task A and Task B (machine- and human-readable).
3. `AGENTS.md` migrated/expanded from `.github/copilot-instructions.md`.
4. Custom **review droid** under `.factory/droids/`.
5. Worked example: execute Task A end-to-end, produce the PR + scorecard entry.
6. Worked example: execute Task B end-to-end, produce the PR + scorecard entry.
7. `demo/baseline/` capture instructions + placeholders for your recorded run.

---

*This runbook is the script. Nothing in the product has been changed yet — the build backlog above
executes only after your review.*
