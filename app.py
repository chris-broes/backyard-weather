from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import re
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
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

MAPCLICK_URL = "https://forecast.weather.gov/MapClick.php?lat=37.7749&lon=-122.4194"
LOCAL_WEATHER_URL = "https://www.weather.gov/wrh/localweather?zone=CAZ006"
STATION_ID = "CW5988"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

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
    temperature = SelectField(
        'Temperature (°F)',
        choices=[
            ('-10', '-10°F'),
            ('-5', '-5°F'),
            ('0', '0°F'),
            ('5', '5°F'),
            ('15', '15°F'),
            ('32', '32°F'),
            ('50', '50°F'),
            ('64', '64°F'),
            ('75', '75°F'),
            ('90', '90°F'),
        ],
        validators=[DataRequired()],
    )
    temperature_feels = SelectField(
        'Temperature Feels',
        choices=[
            ('Hot', 'Hot'),
            ('Warm', 'Warm'),
            ('Cool', 'Cool'),
            ('Cold', 'Cold'),
            ('Frigid', 'Frigid'),
        ],
        validators=[DataRequired()],
    )
    vibe = SelectField(
        'Vibe',
        choices=[
            ('Sweltering', 'Sweltering'),
            ('Hot', 'Hot'),
            ('Nice', 'Nice'),
            ('Jacket', 'Jacket'),
            ('Too Cold', 'Too Cold'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Save Entry')

def _parse_float(value: str) -> Optional[float]:
    match = re.search(r"\d+(?:\.\d+)?", value)
    if not match:
        return None
    return float(match.group(0))


def _parse_wind(text: str) -> tuple[Optional[float], Optional[str]]:
    wind_text = text.strip().upper()
    if not wind_text or wind_text == 'NA':
        return None, None

    direction_match = re.search(r"\b([NSEW]{1,3})\b", wind_text)
    speed_match = re.search(r"(\d+(?:\.\d+)?)", wind_text)

    direction = direction_match.group(1) if direction_match else None
    speed = float(speed_match.group(1)) if speed_match else None
    return speed, direction


def _normalize_wind_direction(text: str) -> Optional[str]:
    raw = text.strip().upper()
    if not raw:
        return None
    if re.fullmatch(r"[NSEW]{1,3}", raw):
        return raw

    mapping = {
        'NORTH': 'N',
        'SOUTH': 'S',
        'EAST': 'E',
        'WEST': 'W',
        'NORTHEAST': 'NE',
        'NORTHWEST': 'NW',
        'SOUTHEAST': 'SE',
        'SOUTHWEST': 'SW',
        'VARIABLE': 'VRB',
    }
    return mapping.get(raw)


def _parse_mapclick_weather(soup: BeautifulSoup) -> tuple[Optional[float], Optional[str], Optional[float], Optional[float], Optional[float], Optional[str]]:
    details: dict[str, str] = {}
    for row in soup.select('table#current_conditions_detail tr'):
        cells = row.find_all(['th', 'td'])
        if len(cells) != 2:
            continue
        key = cells[0].get_text(' ', strip=True).rstrip(':').lower()
        details[key] = cells[1].get_text(' ', strip=True)

    temp_text = None
    temp_el = soup.select_one('#current_conditions-summary .myforecast-current-lrg')
    if temp_el:
        temp_text = temp_el.get_text(' ', strip=True)
    if not temp_text:
        temp_text = details.get('temperature', '')

    desc = None
    desc_el = soup.select_one('#current_conditions-summary .myforecast-current')
    if desc_el:
        desc = desc_el.get_text(' ', strip=True)
    if not desc:
        desc = details.get('weather')

    pressure = _parse_float(details.get('barometer', '') or details.get('pressure', ''))
    humidity = _parse_float(details.get('humidity', ''))
    wind_speed = _parse_float(details.get('wind speed', ''))
    wind_direction = None

    wind_dir_text = details.get('wind direction', '')
    if wind_dir_text:
        wind_direction = _normalize_wind_direction(wind_dir_text)

    if wind_speed is None or wind_direction is None:
        fallback_speed, fallback_dir = _parse_wind(details.get('wind', ''))
        if wind_speed is None:
            wind_speed = fallback_speed
        if wind_direction is None:
            wind_direction = fallback_dir

    return _parse_float(temp_text or ''), desc, pressure, wind_speed, humidity, wind_direction


def _parse_local_weather_table(soup: BeautifulSoup) -> tuple[Optional[float], Optional[str], Optional[float], Optional[float], Optional[float], Optional[str]]:
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 8:
            continue

        location_text = cells[0].get_text(' ', strip=True)
        if STATION_ID not in location_text:
            continue

        temp_val = _parse_float(cells[2].get_text(' ', strip=True))
        humidity = _parse_float(cells[4].get_text(' ', strip=True))
        desc = cells[5].get_text(' ', strip=True) or None
        wind_speed, wind_direction = _parse_wind(cells[6].get_text(' ', strip=True))
        pressure = _parse_float(cells[7].get_text(' ', strip=True))
        return temp_val, desc, pressure, wind_speed, humidity, wind_direction

    return None, None, None, None, None, None

def get_weather() -> tuple[Optional[float], Optional[str], Optional[float], Optional[float], Optional[float], Optional[str]]:
    for url, parser in (
        (MAPCLICK_URL, _parse_mapclick_weather),
        (LOCAL_WEATHER_URL, _parse_local_weather_table),
    ):
        try:
            response = requests.get(url, timeout=20, headers=REQUEST_HEADERS)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Weather request to %s failed: %s", url, exc)
            continue

        try:
            parsed = parser(BeautifulSoup(response.content, 'html.parser'))
        except Exception as exc:
            logger.warning("Failed to parse weather data from %s: %s", url, exc)
            continue

        if parsed[0] is not None:
            return parsed
        logger.info("No usable weather data found at %s", url)

    logger.error("All weather sources failed to return usable data")
    return None, None, None, None, None, None

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
        try:
            db.session.add(weather)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("Failed to save fetched weather entry: %s", exc)
            return "Failed to save weather", 500
        return redirect(url_for('index'))
    return "Failed to fetch weather", 500

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = WeatherForm()
    if form.validate_on_submit():
        temp = _parse_float(form.temperature.data)
        if temp is None:
            return "Invalid temperature", 400

        now = datetime.now()
        weather = Weather(
            date=now.date(),
            time=now.time(),
            temperature=temp,
            description=None,
            temperature_feels=form.temperature_feels.data,
            vibe=form.vibe.data,
            pressure=None,
            wind_speed=None,
            humidity=None,
            wind_direction=None,
        )
        try:
            db.session.add(weather)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("Failed to save weather entry: %s", exc)
            return "Failed to save weather", 500
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))