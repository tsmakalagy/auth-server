#!/bin/sh
set -e

echo "Starting Flask application..."
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --log-level=info --access-logfile - --error-logfile - "app:app"