# LedgerLine

A consumer fintech demo suite: track personal finances, auto-categorize
spending, and get rules-based financial product recommendations.

## Services

- **ledger** (repo root) — Flask app: post transactions (charges and
  refunds/credits), auto-categorize from descriptions, see a running balance
  and a spending-insights view. SQLite by default, Postgres-ready via
  `DATABASE_URL`.
- **reminders** (`reminders/`) — aiohttp microservice with a static front end
  for payment reminders.
- **recommendations** (`recommendations/`) — aiohttp microservice that turns a
  spending profile into explainable product recommendations (cashback card,
  high-yield savings, subscription optimizer, ...).

## Run

```bash
pip install -r requirements.txt
FLASK_APP=app.py flask db upgrade
SECRET_KEY=dev python app.py          # ledger on :5000
python reminders/app.py               # reminders on :8001
python recommendations/app.py         # recommendations on :8002
```

Or with containers:

```bash
SECRET_KEY=dev docker compose up --build   # ledger :8000, reminders :8001, recommendations :8002
```

## Testing

```bash
python -m pytest -q
flake8 . --max-line-length=127 --exclude=.venv,migrations,__pycache__
```
