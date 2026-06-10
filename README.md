# LedgerLine

A consumer fintech demo app: a transactions ledger with a running balance, plus
a payment-reminders microservice.

## Services

- **ledger** (repo root) — Flask app: post transactions (charges and
  refunds/credits), tag categories, see a running balance. SQLite by default,
  Postgres-ready via `DATABASE_URL`.
- **reminders** (`reminders/`) — aiohttp microservice with a static front end
  for payment reminders.

## Run

```bash
pip install -r requirements.txt
FLASK_APP=app.py flask db upgrade
SECRET_KEY=dev python app.py          # ledger on :5000
python reminders/app.py               # reminders on :8001
```

Or with containers:

```bash
SECRET_KEY=dev docker compose up --build   # ledger :8000, reminders :8001
```

## Testing

```bash
python -m pytest -q
flake8 . --max-line-length=127 --exclude=.venv,migrations,__pycache__
```
