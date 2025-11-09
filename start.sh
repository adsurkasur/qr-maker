#!/usr/bin/env bash
# Start script for production: uses gunicorn to serve the Flask app
# Bind to the PORT environment variable (set by hosting platforms). Defaults to 7860.
PORT=${PORT:-7860}

echo "Starting gunicorn on 0.0.0.0:${PORT}..."
exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120 app:app
