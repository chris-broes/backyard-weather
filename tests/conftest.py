import os

# Point the app at an isolated test database BEFORE app.py is imported.
# Flask-SQLAlchemy binds its engine at import time, so the database URL must be
# set via the environment here (conftest runs before any test module imports
# `app`). Without this, db.create_all()/db.drop_all() in fixtures would operate
# on the development weather.db and destroy real data.
_TEST_DB = os.path.join(os.path.dirname(__file__), 'test.db')
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + _TEST_DB)
os.environ.setdefault('SECRET_KEY', 'test-insecure-key')
os.environ.setdefault('FLASK_ENV', 'testing')
