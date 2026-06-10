# AGENTS.md — LedgerLine

Project context for Factory Droid (and any coding agent) working in this repo.

## What this is
**LedgerLine**, a consumer fintech app (personal finance / payments), built as
two small services:

- **ledger** (repo root) — Flask web app: a transactions ledger with manual
  entry, category tagging, and a running balance. Persistence is SQLite
  (`ledgerline.db`), Postgres-ready via `DATABASE_URL`.
- **reminders** (`reminders/`) — aiohttp microservice + static front end for
  payment reminders (create, complete, delete).

Usability and correctness of money math are the product's differentiators.

## Commands
- Install: `pip install -r requirements.txt`
- Run ledger: `SECRET_KEY=dev python app.py` (refuses to boot without `SECRET_KEY`)
- Run reminders: `python reminders/app.py` (port 8001)
- Run both (containers): `SECRET_KEY=dev docker compose up --build`
- Tests: `python -m pytest -q`
- Lint: `flake8 . --max-line-length=127 --exclude=.venv,migrations,__pycache__`
- Security scan: `bandit -r . -x ./.venv,./tests,./migrations`

## Key files
- `app.py` — ledger service: `Transaction` model, routes (`/`, `/add`, `/health`),
  amount parsing.
- `config.py` — env-driven config; supports `DATABASE_URL` (sqlite default,
  Postgres-ready).
- `reminders/app.py` — reminders API; `reminders/static/index.html` — its UI.
- `templates/` — ledger Jinja templates. `tests/` — pytest suite for both
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
- Amounts are USD floats in the model; **negative = credit/refund, positive =
  charge**. Sign integrity is critical: a dropped minus sign corrupts balances.
- Display: charges as `$X.XX`, credits as `-$X.XX` (rendered green). Balance is
  the signed sum of all transactions.
- Reminders are intentionally simple: `title` + `completed`. Validate input at
  the API boundary; reject reminders without a meaningful title.
- The reminders service holds state in memory by design (demo scope); do not
  add a database to it unless a ticket explicitly asks.

## Definition of Done (default)
A change is done when: the feature works end-to-end, inputs are validated,
`pytest` is green, `flake8` is clean, no new bandit/CodeQL findings, and the
change is a single reviewable unit.
