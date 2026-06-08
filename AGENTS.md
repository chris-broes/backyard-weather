# AGENTS.md — python_weather

Project context for Factory Droid (and any coding agent) working in this repo.
Mirrors and supersedes `.github/copilot-instructions.md` so every agent shares
the same conventions.

## What this is
A Flask web app that produces an **insurance weather risk score** from
user-reported inputs and local weather-station data. The risk score is the
product's differentiator. Persistence is SQLite (`weather.db`); current
conditions come from weather.gov.

## Commands
- Install (runtime): `pip install -r requirements.txt`
- Install (dev/tooling): `pip install -r requirements-dev.txt`
- Run: `SECRET_KEY=dev python app.py` (the app refuses to boot without `SECRET_KEY`)
- Tests: `python -m pytest -q`
- Lint: `flake8 . --max-line-length=127`
- Security scan: `bandit -r . -x ./.venv,./tests,./migrations`

## Key files
- `app.py` — Flask app: models, routes (`/`, `/add`, `/fetch`, `/health`), weather parsing.
- `risk_scoring.py` — risk-scoring logic (importable module; no hyphen).
- `config.py` — env-driven config; supports `DATABASE_URL` (sqlite default, Postgres-ready).
- `templates/` — Jinja templates. `tests/` — pytest suite. `migrations/` — Alembic.
- `demo/` — the Droid-vs-baseline measurement program. **Do not modify `demo/`
  when implementing product features** (it's evaluation tooling, not the product).

## Conventions
- Python type hints everywhere they help; clean, idiomatic, Google Python Style.
- Add tests for new behavior; keep `pytest` green before finishing.
- Keep form/template logic simple and maintainable.
- Comments: only for non-obvious reasoning (constraints, invariants, workarounds).
  Do not narrate what the code does; let names and structure carry it.
- Never commit secrets. `SECRET_KEY` and `DATABASE_URL` come from the environment.
- Don't run Flask with `debug=True` in committed code.

## Domain notes
- Weather fields normalized to: temperature °F, pressure inHg, wind speed mph,
  wind direction (compass), humidity %.
- Risk scoring combines temperature, humidity, and wind (extensible to
  precipitation and active NWS alerts). Higher score = higher risk; expose a
  human-readable band (Low/Moderate/High) alongside the numeric score.
- Outbound HTTP should target weather.gov / api.weather.gov only; validate hosts
  before fetching (SSRF hygiene).

## Definition of Done (default)
A change is done when: the feature works end-to-end, inputs are validated,
`pytest` is green, `flake8` is clean, no new bandit/CodeQL findings, and the
change is a single reviewable unit. Phase-specific DoDs live in
`demo/PROGRAM.md` and `demo/RUNBOOK.md`.
