# Talk track — Droid-only demo (`python_weather`)

A spoken narration for a **solo Droid demo** (no live Copilot side-by-side). The
contrast is *narrated*: at each step, a **⚠ Friction** callout names where a
non-agentic workflow — e.g., Copilot in your editor — would hand the work back to
a person.

- **Legend:** `[SAY]` = spoken line (adapt freely) · `[SHOW]` = on screen ·
  `[DO]` = action · **⚠ Friction** = the non-agentic cost you're removing.
- **Total:** ~12–15 min. Layer 1 (proven results) ~5 min · Layer 2 (live) ~6–7 min.
- **Honesty rules (keep them):** same model both arms (**Claude Opus 4.8**); concede
  the speed tie; bug-1 is a *tie* on the fix; say what's **live vs narrated**.
- **Setup:** see `RUNBOOK.md` §0/§9b. Have the DECK open, `gh issue 13` ready,
  `droid/bug-1/run-01` clean, terminal font large.

---

## 0 · Cold open (~45s)

[SAY] "Everyone can demo 'AI writes code' — that's table stakes now. I want to show
you something different: how much of the **engineering workflow *around* the code**
an agent platform takes off your team, and what that does to **quality** and
**predictability**. Everything you'll see is Droid. As we go, I'll point out where a
traditional, non-agentic setup — say Copilot in your editor — puts the work back on
a person."

[SHOW] The repo + the deck title slide.

---

## 1 · Method, up front (~45s)  ·  DECK Slides 1–2

[SAY] "Thirty seconds on method, because the first reaction to any benchmark is
'it's rigged.' Same repo, same frozen tasks, same prompts — and the **same
underlying model, Claude Opus 4.8**, on both a mainstream assistant and Droid. So
anything we see is the **tool and the workflow, not the model**. Every run is
auto-measured by a harness that's in this repo, and a neutral reviewer graded both
sides. You can re-run all of it yourselves."

---

## 2 · Layer 1 — the proven feature work (~3–4 min)

> This is the evidence the demo rests on: real application improvements, measured.

### 2a · Build a feature: risk-scoring core  ·  DECK Slide 3
[SAY] "First, *building a feature* — the risk-scoring core that's this product's
differentiator. Same model, same prompt. I'll concede something right away: the
baseline was a touch faster on the clock. But Droid shipped **2× the tests, +8
points of coverage, and lint-clean**. Both 'passed' the definition of done — only
one of them is code you'd want to be on call for."

**⚠ Friction (non-agentic):** "This is the gap between an engineer who, under
deadline, writes the happy-path test and moves on — and edge cases getting covered
**every time** because the standard is enforced, not remembered."

### 2b · A real migration: HTML scrape → NWS JSON API  ·  DECK Slide 4
[SAY] "Then a real migration — ripping out brittle HTML scraping for the NWS JSON
API. We ran it **three times per arm** to be honest about variance. Speed was a
**tie**, within noise — I won't claim Droid is faster. The story is two things:
**thoroughness** — 2.3× the tests, nearly +8 points coverage — and
**predictability**. Droid lands ~39 tests and ~89% coverage in about 490 seconds,
**every time, ±31 seconds**. The baseline was a coin flip — one run 330 seconds,
another 789. Enterprises plan against the worst case, and that variance is a tax."

**⚠ Friction:** "Inconsistency *is* the cost. A workflow you can't estimate is a
workflow you can't staff."

### 2c · Why thoroughness pays: the caught latent bug  ·  DECK Slide 5
[SAY] "And here's why coverage isn't a vanity number. The neutral reviewer found a
**real latent bug** in the baseline's migration: pressure normalization used
`barometricPressure or seaLevelPressure`. In live NWS data that first field is
usually **present but null** — a truthy object — so the fallback never fires and
**pressure silently goes missing on real data**. The baseline's own tests passed,
because its fixture was fully populated. **That bug ships.** Droid's broader
edge-case tests are exactly what catch this class of defect. And to be fair — the
same reviewer also dinged *Droid* for an SSRF-redirect hardening nit. It's not
rubber-stamping either side."

**⚠ Friction:** "Without an agent enforcing edge-case coverage and an automated
review in the loop, this is a 2 a.m. page — it escapes to production."

---

## 3 · The pivot (~45s)

[SAY] "So Layer 1 — *building software* — Droid delivers more production-ready code,
more predictably, at the same model and the same speed. Now the half most demos
skip: **everything that happens around a code change.**"

[SAY — the key talking point] "**Bugs show up in any codebase.** This next one is
trivial — a one-line fix any tool nails identically. And that's exactly the point:
**the fix was never the expensive part.** What costs development teams real cycles
is all the *friction around* it — triaging the ticket, reproducing, writing the
test, opening the PR, chasing a first review, updating the tracker. Multiply that by
every routine bug, every week. **With Droid I can automate fixes like this
end-to-end — but only inside the criteria *I* set in `AGENTS.md`.** I decide what's
safe to hand off and what every fix must satisfy. Watch."

[SHOW — optional] The relevant `AGENTS.md` criteria, e.g.:
- **Scope that qualifies for hands-off:** localized fixes — parsing, validation,
  null/edge-case handling — **no** schema, API-contract, or auth changes.
- **Every fix must:** add a regression test first, follow our conventions
  (units, SSRF, no debug), be a single reviewable unit.
- **Gates before merge:** full suite green, lint clean, no new bandit/CodeQL
  findings, **and human approval on the PR.**

[SAY] "Anything outside those rules escalates to a person. This isn't an agent run
loose — it's an agent running *my* playbook, consistently. The fix is a **tie**;
the **policy-driven workflow** is the difference."

---

## 4 · Layer 2 — live: bug to merged PR, hands-off (~6–7 min)

### Beat 1 · The incident enters  ·  [DO] open GitHub Issue #13
[SAY] "A bug report lands: **negative temperatures are being stored as positive** —
a data-quality defect that corrupts our risk scores. Here it's a GitHub issue; in
your world it's Sentry, Jira, Linear, or a Slack message. The work enters where the
report lives."

**⚠ Friction:** "Normally *this* is where an engineer reads the ticket, context-
switches into the editor, and starts reproducing by hand."

### Beat 2 · One trigger → Droid does the whole fix  ·  [DO] kick off Droid (headless / from the issue)
[SAY] "I give Droid **one instruction** — fix this issue — and step back. It
reproduces the bug, **writes a regression test first**, then the fix — applying the
**exact criteria I just showed you in `AGENTS.md`**: it confirms this is an in-scope,
localized fix, follows our conventions (units, SSRF, no debug), and holds itself to
our definition of done. I'm not re-explaining any of that, and I'm not hoping it
remembered — the policy is enforced."

**⚠ Friction:** "In a Copilot-style flow the model suggests a diff — but **the
engineer** owns remembering the conventions, writing the regression test, and
deciding what 'done' means. Done well on a good day, skipped on a busy one. Here
it's identical every time."

### Beat 3 · A well-formed, linked PR  ·  [DO] show the PR (`Fixes #13`, summary + test plan)
[SAY] "Now it opens a pull request — with a written summary and a test plan — and
**links it to the issue**. I didn't write that description or wire up the linkage."

**⚠ Friction:** "That's the alt-tab-to-GitHub, hand-write-the-PR-body,
remember-to-type-'Fixes #13' ritual — gone."

### Beat 4 · Governed review + gates  ·  [DO] reviewer droid + `review-pr.sh`; CI runs (CodeQL narrate)
[SAY] "The instant the PR is up, a **review droid** — a versioned, org-shared
specialist, the same neutral reviewer from our scorecard — reviews the diff and
posts its findings **right on the PR**. CI runs tests and lint automatically; on
PRs to main, CodeQL adds a security scan. A human still makes the final call — but
they walk up to a PR that's already **triaged, tested, and reviewed**."

**⚠ Friction:** "Otherwise the PR sits waiting for a human to find time for a first
pass. First-pass review is the classic bottleneck — here it's instant and
consistent."

### Beat 5 · Close the loop  ·  [DO] merge → issue #13 auto-closes
[SAY] "On merge, the **issue closes itself** and stakeholders are notified — Slack,
the ticket, however you wire it. The loop closes with nobody updating a status
field."

**⚠ Friction:** "The 'don't forget to close the ticket and tell people' step —
automated."

---

## 5 · Close (~60s)

[SAY] "Step back. A terminal assistant and Droid both write that one-line fix — same
model, same patch. The difference is **everything else**: from one trigger, Droid
ran the whole incident — reproduced it, tested it to our standards, opened a linked
PR, got it reviewed and gated, and closed the loop. That's **hours of connective-
tissue work, done consistently**, that normally lands on your engineers between the
'real' work. Put it next to Layer 1 — more production-ready features, more
predictably — and the thesis is simple: **the quality compounds and the workflow
overhead collapses**. Same model as anyone else; the difference is the **platform
around it**."

[SAY — governance nod] "And because it's a platform: this model **or your own** via
BYOK, **role-scoped droids your org shares**, and **every action audited** — it fits
how an enterprise actually governs this."

[SAY — close] "Happy to point any of this at *your* repo and *your* tracker — that's
the real test."

---

## Appendix · Live-vs-narrated cheat sheet
- **Live today:** GitHub issue, Droid fix + regression test, linked PR, review droid
  comment, CI (tests/lint).
- **Narrate (unless configured):** CodeQL (runs on PRs to `main` only), Sentry/Jira/
  Linear intake, Slack/ChatOps trigger, BYOK/audit governance.
- **If asked "is this just the model?":** both arms ran Opus 4.8 — it's the tool and
  the workflow, not the LLM.
- **If asked "N is small":** correct — directional, one repo; the harness is yours to
  re-run at scale.
