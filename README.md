# Weather Tracker

A simple Flask web application to track weather inputs at home.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python app.py`

The app will run on http://127.0.0.1:5000/

## Features

- View list of weather entries with date and time
- Add new weather entries manually with qualitative dropdowns for temperature feel and vibe; numeric weather details are fetched from weather.gov
- Fetch current weather data from weather.gov local weather observations for San Francisco (station CW5988), including temperature in °F, pressure in Hg, wind speed in mph, wind direction, and humidity in %

## Testing

Run the functional test suite: `python -m pytest`

This ensures the app works correctly on launch.