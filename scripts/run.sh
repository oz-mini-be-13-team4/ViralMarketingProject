#!/bin/sh
set -e

echo "=== Running Django migrations ==="
/root/.local/bin/poetry run python manage.py makemigrations --noinput || true
/root/.local/bin/poetry run python manage.py migrate --noinput

echo "=== Starting Gunicorn server ==="
/root/.local/bin/poetry run gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2