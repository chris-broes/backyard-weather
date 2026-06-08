# Factory Droid vs. Baseline — a measured head-to-head
### `python_weather`: an insurance weather risk-scoring app
*Snapshot as of 2026-06-05 · 2 phases complete · reproducible harness in `demo/`*

> Speaker note: The promise isn't "AI writes code." Everyone has that. The
> promise we're testing is **production-readiness per unit of engineering time** —
> and whether that advantage **compounds** as a codebase grows.

---

## Slide 1 — The question we actually measured

Not "is it faster to type?" but: **for the same task and the same Definition of
Done, which tool produces more production-ready software, more predictably?**

We ran a controlled bake-off:
- **Same repo, same frozen tasks, same prompts** handed to both arms.
- **Baseline arm** = a mainstream AI coding assistant (Copilot-style).
- **Droid arm** = Factory Droid.
- **Same underlying model on both arms — Claude Opus 4.8** — so we isolate the
  *tool/agent*, not the LLM.
- Every run **auto-measured** by a harness; a **neutral reviewer** graded both.

> Speaker note: Lead with the method, because a technical buyer's first instinct
> is "your benchmark is rigged." We hand them the harness.

---

## Slide 2 — How we kept it honest

| Guardrail | What it means |
|---|---|
| Frozen tasks + identical prompts | Both arms get the *exact* same ask (`demo/PROMPTS.md`) |
| Same underlying model | Both arms ran **Claude Opus 4.8** — isolates the tool/agent, not the LLM |
| Executable Definition of Done | A grader script decides "done," not opinion (`demo/dod/`) |
| Auto-collected metrics | Time, tests, coverage, lint, security — no hand-entry (`demo/measure.py`) |
| Neutral referee | One reviewer rubric applied to **both** diffs, blind to author |
| Multiple samples | Phase 2 run **3× per arm** to expose variance, not cherry-pick |
| Full reproducibility | Every run is a JSON record on a git branch; re-runnable |

> Speaker note: This slide is the credibility anchor. The numbers only matter if
> the method survives scrutiny.

---

## Slide 3 — Phase 1: build a feature (risk-scoring core)

*N=1 per arm — directional.*

| Metric | Baseline | Droid |
|---|---|---|
| Time to done | 403s | 484s |
| Tests added | 9 | **19** |
| Coverage | 74.0% | **82.2%** |
| Tests / min | 0.89 | **1.98** |
| Lint (flake8) | 2 | **0** |
| Definition of Done | full | full |

**Takeaway:** Baseline was slightly faster on the clock; Droid delivered **2×
the tests, +8 pts coverage, lint-clean** — both met the bar, Droid exceeded it.

> Speaker note: We *concede* the clock here on purpose. It sets up Phase 2 and
> signals we're not spinning.

---

## Slide 4 — Phase 2: a real migration (HTML scrape → NWS JSON API)

*N=3 per arm — the honest comparison.*

| Metric | Baseline (mean) | Droid (mean) | Edge |
|---|---|---|---|
| Time to done | 514s | 494s | ~tie |
| **Consistency** (std dev) | **±198s** (330–789) | **±31s** (458–534) | **Droid 6× steadier** |
| Tests added | 17 | **39** | **2.3×** |
| Coverage | 80.9% | **88.8%** | **+7.9 pts** |
| Tests / min | 1.79 | **4.40** | **2.5×** |
| Lint (flake8) | 1 | **0** | Droid |
| Definition of Done | full | full | tie |

**Two findings that survive scrutiny:**
1. **Speed is a tie** (4%, within noise). We will *not* claim Droid is faster here.
2. The real gap is **thoroughness at equal speed** + **predictability**: Droid
   reliably ships ~39 tests / ~89% coverage in ~490s; the baseline is a gamble
   (one run 330s/15 tests, another 789s/17 tests).

> Speaker note: The variance story is underrated. Enterprises plan against the
> *worst* case. ±31s vs ±198s is an estimation/quality argument, not a vanity stat.

---

## Slide 5 — The proof that thoroughness = fewer escaped bugs

A **neutral reviewer** (same rubric, both arms) reviewed the Phase-2 diffs:

| | Findings | Blocking (crit/high) | Headline |
|---|---|---|---|
| Droid | 3 | 0 | only minor hardening/style notes |
| Baseline | 5 | 0 | **1 real latent correctness bug** |

**The latent bug (baseline):** pressure normalization used
`barometricPressure or seaLevelPressure`. In real NWS payloads `barometricPressure`
is usually present-but-`null` — a *truthy* object — so the fallback never fires
and **pressure silently goes missing on live data**. Baseline's test fixture was
fully populated, so **its own tests passed and the bug would ship.**

Droid's broader edge-case tests are exactly what prevent this class of defect.

> Speaker note: This is the emotional peak. The coverage gap wasn't a vanity
> number — it *manifested* as a shipped defect in the other arm. "More
> production-ready," demonstrated, not asserted. Note the referee also dinged
> Droid (SSRF redirect hardening) — it's not rubber-stamping.

---

## Slide 6 — What we are *not* claiming (so you can trust what we are)

- **Not** "Droid is dramatically faster" — on these tasks, time-to-done is ~even.
- **Not** a large-scale study — single repo, one operator, small N (directional).
- **Not** "more code is better" — the extra tests are backed by **measured
  coverage** and a **caught bug**, not padding.
- **Not** a model comparison — **both arms ran the same model (Claude Opus 4.8)**,
  so every difference is attributable to the **tool/agent**, not the LLM.

**What we *are* claiming, with evidence:** same speed, **materially more
production-ready output** (tests, coverage, lint, a caught latent bug), delivered
**far more predictably** — at parity on the underlying model.

> Speaker note: Volunteering the limits is what makes the claims land. This slide
> wins the skeptics in the room.

---

## Slide 7 — Why this compounds (the thesis + what's next)

Quality and production-readiness **compound**: every phase Droid builds on a
cleaner, better-tested base, while latent defects and thin tests **accumulate
risk** on the other side.

**Roadmap (this same harness, fully scoped in `demo/PROGRAM.md`):**
- Feature phases p2–p9 (multi-location, alerts, configurable model, REST API,
  multi-tenant, Postgres migration, security hardening, bulk scoring).
- A **seeded production bug** → live **time-to-fix** head-to-head.
- Each phase advances the track, so the gap is measured **cumulatively**.

> Speaker note: This is the hook to keep the engagement going — and the live
> demo (the seeded-bug fix) is where the room feels it in real time.

---

## Appendix — Reproduce it yourself

```bash
.venv/bin/python demo/measure.py shell      # interactive harness
> aggregate --task task-b                    # regenerates the Phase-2 table
> aggregate                                  # all phases, pooled
```
- Per-run records: `demo/results/runs/*.json`
- Generated summaries: `demo/results/summary_*.md`
- Method + tasks: `demo/PROGRAM.md`, `demo/PROMPTS.md`, `demo/MEASURE.md`
