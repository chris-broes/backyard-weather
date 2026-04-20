from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import re
from sqlalchemy import inspect, text
from typing import Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'weather.db')
db = SQLAlchemy(app)

WU_URL = "https://www.wunderground.com/weather/us/ca/san-francisco/KCASANFR107"
WU_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    temperature_feels = db.Column(db.String(20))
    vibe = db.Column(db.String(20))
    pressure = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_direction = db.Column(db.String(20))

class WeatherForm(FlaskForm):
    temperature_feels = SelectField(
        'Temperature Feels',
        choices=[
            ('Hot', '🔥 Hot'),
            ('Warm', '☀️ Warm'),
            ('Cool', '🌤️ Cool'),
            ('Cold', '🧊 Cold'),
            ('Frigid', '🥶 Frigid'),
        ],
        validators=[DataRequired()],
    )
    vibe = SelectField(
        'Vibe',
        choices=[
            ('Sweltering', '😓 Sweltering'),
            ('Hot', '🥵 Hot'),
            ('Nice', '😊 Nice'),
            ('Jacket', '🧥 Jacket'),
            ('Too Cold', '🌨️ Too Cold'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Save Entry')

def _parse_wu_wind(text: str) -> tuple[Optional[float], Optional[str]]:
    """Parse wind text like 'N 1 Gusts 7 ° mph' into (speed, direction)."""
    text = text.strip()
    m = re.match(r'([NSEW]{1,3})\s+(\d+(?:\.\d+)?)', text)
    if m:
        return float(m.group(2)), m.group(1)
    m = re.search(r'(\d+(?:\.\d+)?)', text)
    if m:
        return float(m.group(1)), None
    return None, None

def _wu_value(soup: BeautifulSoup, type_name: str) -> Optional[float]:
    el = soup.select_one(f'[type="{type_name}"] .wu-value-to')
    if el:
        try:
            return float(el.get_text(strip=True))
        except ValueError:
            return None
    return None

def get_weather() -> tuple[Optional[float], Optional[str], Optional[float], Optional[float], Optional[float], Optional[str]]:
    headers = {'User-Agent': WU_USER_AGENT}
    response = requests.get(WU_URL, timeout=20, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    temp_el = soup.select_one('.current-temp .wu-value-to')
    temp = float(temp_el.get_text(strip=True)) if temp_el else None

    desc_el = soup.select_one('lib-city-current-conditions .condition-icon p')
    desc = desc_el.get_text(strip=True) if desc_el else None

    wind_el = soup.select_one('.condition-wind')
    wind_speed, wind_direction = _parse_wu_wind(wind_el.get_text(' ', strip=True)) if wind_el else (None, None)

    pressure = _wu_value(soup, 'pressure')
    humidity = _wu_value(soup, 'humidity')

    return temp, desc, pressure, wind_speed, humidity, wind_direction

def ensure_schema():
    inspector = inspect(db.engine)
    if not inspector.has_table('weather'):
        db.create_all()
        return

    columns = {col['name'] for col in inspector.get_columns('weather')}
    updates = []
    if 'time' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN time TEXT")
    if 'temperature_feels' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN temperature_feels TEXT")
    if 'vibe' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN vibe TEXT")
    if 'pressure' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN pressure FLOAT")
    if 'wind_speed' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN wind_speed FLOAT")
    if 'humidity' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN humidity FLOAT")
    if 'wind_direction' not in columns:
        updates.append("ALTER TABLE weather ADD COLUMN wind_direction TEXT")

    if updates:
        with db.engine.begin() as conn:
            for stmt in updates:
                conn.execute(text(stmt))

@app.route('/')
def index():
    ensure_schema()
    weathers = Weather.query.order_by(Weather.date.desc(), Weather.time.desc()).all()
    return render_template('index.html', weathers=weathers)

@app.route('/fetch')
def fetch():
    temp, desc, pressure, wind_speed, humidity, wind_direction = get_weather()
    if temp is not None:
        now = datetime.now()
        weather = Weather(
            date=now.date(),
            time=now.time(),
            temperature=temp,
            description=desc,
            temperature_feels=None,
            vibe=None,
            pressure=pressure,
            wind_speed=wind_speed,
            humidity=humidity,
            wind_direction=wind_direction,
        )
        db.session.add(weather)
        db.session.commit()
        return redirect(url_for('index'))
    return "Failed to fetch weather", 500

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = WeatherForm()
    if form.validate_on_submit():
        temp, desc, pressure, wind_speed, humidity, wind_direction = get_weather()
        if temp is None:
            return "Failed to fetch weather", 500

        now = datetime.now()
        weather = Weather(
            date=now.date(),
            time=now.time(),
            temperature=temp,
            description=desc,
            temperature_feels=form.temperature_feels.data,
            vibe=form.vibe.data,
            pressure=pressure,
            wind_speed=wind_speed,
            humidity=humidity,
            wind_direction=wind_direction,
        )
        db.session.add(weather)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)