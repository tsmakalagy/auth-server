#!/bin/sh
set -e

# Wait for database to be ready
wait-for db:5432 -t 60

# Run migrations if needed
flask db upgrade

# Start the Flask application
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 60 "app:create_app()"