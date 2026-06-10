from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime
import os
import re
import logging
import requests
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from categorize import categorize
from config import config_by_name

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config_by_name[os.environ.get('FLASK_ENV', 'development')])

if not app.config.get('SECRET_KEY'):
    raise RuntimeError(
        "SECRET_KEY is not set. Define the SECRET_KEY environment variable "
        "before starting the app in this environment."
    )

db = SQLAlchemy(app)
migrate = Migrate(app, db)

RECOMMENDATIONS_URL = os.environ.get('RECOMMENDATIONS_URL', 'http://127.0.0.1:8002')

CATEGORIES = [
    ('Auto', 'Auto-detect from description'),
    ('Dining', 'Dining'),
    ('Groceries', 'Groceries'),
    ('Transport', 'Transport'),
    ('Subscriptions', 'Subscriptions'),
    ('Shopping', 'Shopping'),
    ('Refund', 'Refund'),
    ('Income', 'Income'),
    ('Other', 'Other'),
]


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(40), nullable=False)


class TransactionForm(FlaskForm):
    description = StringField(
        'Description',
        validators=[DataRequired(), Length(max=200)],
    )
    amount = StringField(
        'Amount (USD — use a minus sign for refunds/credits, e.g. -5.00)',
        validators=[DataRequired(), Length(max=20)],
    )
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    submit = SubmitField('Post Transaction')


def _parse_amount(value: str) -> Optional[float]:
    match = re.search(r"\d+(?:\.\d+)?", value)
    if not match:
        return None
    return float(match.group(0))


@app.route('/health')
def health():
    try:
        db.session.execute(text('SELECT 1'))
    except SQLAlchemyError as exc:
        logger.error("Health check database probe failed: %s", exc)
        return jsonify(status='error', database='unavailable'), 503
    return jsonify(status='ok', database='ok')


@app.route('/')
def index():
    transactions = Transaction.query.order_by(
        Transaction.date.asc(), Transaction.time.asc()
    ).all()
    balance = sum(txn.amount for txn in transactions)
    return render_template('index.html', transactions=transactions, balance=balance)


def _spending_profile(transactions: list['Transaction']) -> dict:
    category_totals: dict[str, float] = {}
    for txn in transactions:
        if txn.amount > 0:
            category_totals[txn.category] = category_totals.get(txn.category, 0.0) + txn.amount
    return {
        'balance': sum(txn.amount for txn in transactions),
        'category_totals': category_totals,
        'subscription_count': sum(1 for txn in transactions if txn.category == 'Subscriptions'),
    }


def _fetch_recommendations(profile: dict) -> Optional[list[dict]]:
    try:
        response = requests.post(
            f"{RECOMMENDATIONS_URL}/recommendations", json=profile, timeout=3,
        )
        response.raise_for_status()
        return response.json().get('recommendations', [])
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Recommendations service unavailable: %s", exc)
        return None


@app.route('/insights')
def insights():
    transactions = Transaction.query.all()
    profile = _spending_profile(transactions)
    spend_total = sum(profile['category_totals'].values())
    categories = sorted(
        profile['category_totals'].items(), key=lambda item: item[1], reverse=True,
    )
    recommendations = _fetch_recommendations(profile)
    return render_template(
        'insights.html',
        categories=categories,
        spend_total=spend_total,
        balance=profile['balance'],
        recommendations=recommendations,
    )


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = TransactionForm()
    if form.validate_on_submit():
        amount = _parse_amount(form.amount.data)
        if amount is None:
            return "Invalid amount", 400

        category = form.category.data
        if category == 'Auto':
            category = categorize(form.description.data)

        now = datetime.now()
        txn = Transaction(
            date=now.date(),
            time=now.time(),
            description=form.description.data,
            amount=amount,
            category=category,
        )
        try:
            db.session.add(txn)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("Failed to save transaction: %s", exc)
            return "Failed to save transaction", 500
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
