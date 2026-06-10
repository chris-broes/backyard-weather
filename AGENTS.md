# AGENTS.md — LedgerLine

Project context for Factory Droid (and any coding agent) working in this repo.

## What this is
**LedgerLine**, a consumer fintech app (personal finance / payments), built as
three small services:

- **ledger** (repo root) — Flask web app: a transactions ledger with manual
  entry, keyword auto-categorization (`categorize.py`), a running balance, and
  a spending-insights page (`/insights`). Persistence is SQLite
  (`ledgerline.db`), Postgres-ready via `DATABASE_URL`.
- **reminders** (`reminders/`) — aiohttp microservice + static front end for
  payment reminders (create, complete, delete).
- **recommendations** (`recommendations/`) — aiohttp microservice: rules-based
  financial product recommendations from a spending profile (balance, category
  totals, subscription count).

Usability and correctness of money math are the product's differentiators.

## Commands
- Install: `pip install -r requirements.txt`
- Run ledger: `SECRET_KEY=dev python app.py` (refuses to boot without `SECRET_KEY`)
- Run reminders: `python reminders/app.py` (port 8001)
- Run recommendations: `python recommendations/app.py` (port 8002)
- Run all (containers): `SECRET_KEY=dev docker compose up --build`
- Tests: `python -m pytest -q`
- Lint: `flake8 . --max-line-length=127 --exclude=.venv,migrations,__pycache__`
- Security scan: `bandit -r . -x ./.venv,./tests,./migrations`

## Key files
- `app.py` — ledger service: `Transaction` model, routes (`/`, `/add`,
  `/insights`, `/health`), amount parsing, recommendations client.
- `categorize.py` — keyword rules for auto-categorization (order-sensitive).
- `config.py` — env-driven config; supports `DATABASE_URL` (sqlite default,
  Postgres-ready).
- `reminders/app.py` — reminders API; `reminders/static/index.html` — its UI.
- `recommendations/app.py` — product catalog + `recommend()` rules engine.
- `templates/` — ledger Jinja templates. `tests/` — pytest suite for all
  services. `migrations/` — Alembic.

## Conventions
- Python type hints everywhere they help; clean, idiomatic, Google Python Style.
- Add tests for new behavior; keep `pytest` green before finishing.
- Keep form/template logic simple and maintainable.
- Comments: only for non-obvious reasoning (constraints, invariants, workarounds).
  Do not narrate what the code does; let names and structure carry it.
- Never commit secrets. `SECRET_KEY` and `DATABASE_URL` come from the environment.
- Don't run Flask with `debug=True` in committed code.

## Domain notes
- Amounts are USD floats in the model; **negative = purchase/debit (draws down
  the balance), positive = income/credit (increases it)**. Sign integrity is
  critical: a dropped minus sign corrupts balances.
- Display: purchases as `-$X.XX`, income/credits as `+$X.XX` (rendered green).
  Balance is the signed sum of all transactions; the insights chart tracks the
  cumulative balance over time.
- Reminders are intentionally simple: `title` + `completed`. Validate input at
  the API boundary; reject reminders without a meaningful title.
- The reminders and recommendations services hold state in memory by design
  (demo scope); do not add databases to them unless a ticket explicitly asks.
- The ledger must degrade gracefully when the recommendations service is down:
  `/insights` still renders, with recommendations marked unavailable.
- Recommendations are rules-based and explainable: every recommendation carries
  a human-readable `reason` derived from the user's own numbers.
- Cross-service calls go through env-configured URLs (`RECOMMENDATIONS_URL`);
  never hardcode service addresses in logic.

## Definition of Done (default)
A change is done when: the feature works end-to-end, inputs are validated,
`pytest` is green, `flake8` is clean, no new bandit/CodeQL findings, and the
change is a single reviewable unit.
