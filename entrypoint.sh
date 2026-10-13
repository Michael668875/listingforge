#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec python -m gunicorn --bind 0.0.0.0:8000 --workers 3 listingforge.wsgi:application
