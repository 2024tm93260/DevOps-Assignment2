#!/bin/bash
set -e

echo "Starting ACEest Fitness API..."
echo "Environment: ${FLASK_ENV:-production}"
echo "Workers: ${GUNICORN_WORKERS:-2}"
echo "Threads: ${GUNICORN_THREADS:-4}"
echo "Port: ${PORT:-8000}"

# Start Gunicorn
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-30} \
    --keepalive ${GUNICORN_KEEPALIVE:-5} \
    --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
    --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    "app.app:create_app()"