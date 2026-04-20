import pytest
import os
from app import app, db
from unittest.mock import Mock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    test_db_path = os.path.join(os.path.dirname(__file__), '..', 'test.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + test_db_path
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Weather Entries' in response.data


def _mock_weather_response(monkeypatch):
    html = """
    <html><body>
        <lib-city-current-conditions>
            <div class="current-temp">
                <lib-display-unit type="temperature">
                    <span class="wu-unit wu-unit-temperature">
                        <span class="wu-value wu-value-to">64</span>
                    </span>
                </lib-display-unit>
            </div>
            <div class="condition-icon"><p>Mostly Cloudy</p></div>
            <div class="condition-wind small-6 medium-12 columns">SW 8 Gusts 21 ° mph</div>
        </lib-city-current-conditions>
        <lib-display-unit type="pressure">
            <span class="wu-unit"><span class="wu-value wu-value-to">29.85</span></span>
        </lib-display-unit>
        <lib-display-unit type="humidity">
            <span class="wu-unit"><span class="wu-value wu-value-to">56</span></span>
        </lib-display-unit>
    </body></html>
    """
    mock_response = Mock()
    mock_response.content = html.encode('utf-8')
    mock_response.raise_for_status = Mock()
    monkeypatch.setattr('app.requests.get', lambda *args, **kwargs: mock_response)


def test_add_weather(client, monkeypatch):
    _mock_weather_response(monkeypatch)
    response = client.post('/add', data={
        'temperature_feels': 'Cool',
        'vibe': 'Jacket',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'64.0' in response.data
    assert b'Cool' in response.data
    assert b'Jacket' in response.data
    assert b'SW' in response.data


def test_fetch_weather(client, monkeypatch):
    _mock_weather_response(monkeypatch)

    response = client.get('/fetch', follow_redirects=True)
    assert response.status_code == 200
    assert b'Weather Entries' in response.data
    assert b'64.0' in response.data
    assert b'SW' in response.data
    assert b'8.0 mph' in response.data
    assert b'29.85 inHg' in response.data