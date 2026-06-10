from categorize import categorize


def test_dining():
    assert categorize('Blue Bottle Coffee') == 'Dining'


def test_subscriptions():
    assert categorize('Netflix monthly') == 'Subscriptions'


def test_transport():
    assert categorize('Uber trip downtown') == 'Transport'


def test_groceries():
    assert categorize('Whole Foods Market') == 'Groceries'


def test_income():
    assert categorize('ACME Corp payroll') == 'Income'


def test_unknown_falls_back_to_other():
    assert categorize('Mystery vendor 123') == 'Other'
