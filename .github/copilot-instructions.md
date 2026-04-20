# Use this file to provide workspace-specific custom instructions to Copilot.

This repository is a Flask web application for tracking weather entries and optionally scraping current weather data from weather.gov.

## Project overview
- Python Flask app with SQLite persistence (`weather.db`).
- Manual weather entry via `/add` and automated weather fetch via `/fetch`.
- Uses `Flask`, `Flask-SQLAlchemy`, `Flask-WTF`, `requests`, and `beautifulsoup4`.
- Run locally with `python app.py`; app should be available at `http://127.0.0.1:5000/`.
- Tests are executed with `pytest`.

## Copilot guidance
- Use Python type hints when supported.
- Write clean, idiomatic Python consistent with the Google Python Style Guide.
- Keep form handling and template logic simple and maintainable.
- Add tests for new functionality and ensure tests pass before finalizing changes.
- Validate the app's core flow: list entries, add entries, and fetch weather.
- Keep documentation current in `README.md` and this file.
- Do not leave HTML comments in this file.

## Project commands
- Install dependencies: `pip install -r requirements.txt`
- Run the app: `python app.py`
- Run tests: `python -m pytest`

## Project-specific notes
- Weather entries store date, time, temperature, description, pressure, wind speed, and humidity.
- The `/fetch` route scrapes San Francisco weather data from weather.gov and converts barometric pressure to Pascals.
- Use `requirements.txt` for dependency management.
