import pytest
import os
from app import app, db


@pytest.fixture
def client():
    # The test database URL is set in conftest.py via DATABASE_URL before app
    # import, so db here is already bound to tests/test.db (never the dev DB).
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    test_db_path = os.path.join(os.path.dirname(__file__), 'test.db')
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()
        db.session.remove()
        db.engine.dispose()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'LedgerLine' in response.data
    assert b'Current Balance' in response.data


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_add_transaction(client):
    response = client.post('/add', data={
        'description': 'Coffee Shop',
        'amount': '4.50',
        'category': 'Dining',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Coffee Shop' in response.data
    assert b'$4.50' in response.data
    assert b'Dining' in response.data


def test_add_transaction_auto_categorizes(client):
    response = client.post('/add', data={
        'description': 'Netflix monthly',
        'amount': '15.99',
        'category': 'Auto',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Subscriptions' in response.data


def test_insights_renders_with_service_down(client, monkeypatch):
    def _unavailable(*args, **kwargs):
        import requests
        raise requests.ConnectionError('service down')

    monkeypatch.setattr('app.requests.post', _unavailable)
    client.post('/add', data={
        'description': 'Coffee Shop',
        'amount': '4.50',
        'category': 'Dining',
    }, follow_redirects=True)
    response = client.get('/insights')
    assert response.status_code == 200
    assert b'Spending by Category' in response.data
    assert b'Dining' in response.data
    assert b'temporarily unavailable' in response.data


def test_insights_shows_recommendations(client, monkeypatch):
    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {'recommendations': [{
                'name': 'LedgerLine Cashback Card',
                'tagline': '3% back on dining and groceries',
                'reason': 'You spend a lot on dining.',
            }]}

    monkeypatch.setattr('app.requests.post', lambda *a, **k: _FakeResponse())
    response = client.get('/insights')
    assert response.status_code == 200
    assert b'Cashback Card' in response.data


def test_add_transaction_rejects_garbage_amount(client):
    response = client.post('/add', data={
        'description': 'Mystery',
        'amount': 'not-a-number',
        'category': 'Other',
    })
    assert response.status_code == 400
