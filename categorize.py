"""Keyword-based auto-categorization for transaction descriptions."""

# First match wins, so rule order is significant.
RULES: list[tuple[tuple[str, ...], str]] = [
    (('uber', 'lyft', 'transit', 'metro', 'parking', 'shell', 'chevron'), 'Transport'),
    (('coffee', 'cafe', 'restaurant', 'grill', 'pizza', 'doordash', 'grubhub', 'eats', 'bakery', 'bar '), 'Dining'),
    (('grocery', 'market', 'safeway', 'trader', 'whole foods', 'costco'), 'Groceries'),
    (('netflix', 'spotify', 'hulu', 'subscription', 'membership', 'prime', 'icloud'), 'Subscriptions'),
    (('amazon', 'target', 'store', 'shop', 'mall'), 'Shopping'),
    (('refund', 'reversal', 'chargeback'), 'Refund'),
    (('payroll', 'salary', 'deposit', 'interest'), 'Income'),
]

DEFAULT_CATEGORY = 'Other'


def categorize(description: str) -> str:
    normalized = description.lower()
    for keywords, category in RULES:
        if any(keyword in normalized for keyword in keywords):
            return category
    return DEFAULT_CATEGORY
