"""Seed the ledger with a realistic month of demo transactions.

Usage: SECRET_KEY=dev python seed.py
Replaces any existing transactions so reseeding is idempotent.
"""

from datetime import datetime, time, timedelta

from app import app, db, Transaction

# (description, days_ago, hour, amount, category)
# Negative amounts are credits/refunds, positive are charges.
SEED_TRANSACTIONS = [
    ('Uber trip downtown', 1, 18, 18.50, 'Transport'),
    ('Blue Bottle Coffee', 2, 8, 6.50, 'Dining'),
    ('Whole Foods Market', 3, 17, 86.42, 'Groceries'),
    ('Amazon order', 4, 12, 67.84, 'Shopping'),
    ('Golden Gate Grill', 5, 19, 48.75, 'Dining'),
    ('Netflix monthly', 6, 9, 15.99, 'Subscriptions'),
    ('Cashback reward', 7, 10, -12.30, 'Income'),
    ('Spotify Premium', 8, 9, 11.99, 'Subscriptions'),
    ('Slice Pizza Co', 9, 20, 21.40, 'Dining'),
    ("Trader Joe's", 10, 16, 54.17, 'Groceries'),
    ('Target', 11, 14, 39.99, 'Shopping'),
    ('DoorDash dinner', 12, 19, 32.18, 'Dining'),
    ('Refund: returned headphones', 13, 11, -59.99, 'Refund'),
    ('BART transit pass', 14, 7, 64.00, 'Transport'),
    ('iCloud storage', 15, 9, 2.99, 'Subscriptions'),
    ('Safeway', 17, 18, 33.08, 'Groceries'),
    ('Dentist copay', 19, 10, 25.00, 'Other'),
    ('Shell gas station', 20, 15, 41.25, 'Transport'),
    ('Prime membership', 22, 9, 14.99, 'Subscriptions'),
    ('Interest payment', 25, 6, -4.21, 'Income'),
]


def seed() -> None:
    today = datetime.now().date()
    with app.app_context():
        Transaction.query.delete()
        for description, days_ago, hour, amount, category in SEED_TRANSACTIONS:
            db.session.add(Transaction(
                date=today - timedelta(days=days_ago),
                time=time(hour=hour, minute=(days_ago * 7) % 60),
                description=description,
                amount=amount,
                category=category,
            ))
        db.session.commit()
        count = Transaction.query.count()
        balance = sum(txn.amount for txn in Transaction.query.all())
        print(f"Seeded {count} transactions, balance ${balance:.2f}")


if __name__ == '__main__':
    seed()
