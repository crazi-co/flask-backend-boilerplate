#!/bin/bash
set -e

# Get port from environment or default to 5000
PORT=${PORT:-5000}
API_BASE=${API_BASE:-/api/v1}

echo "=========================================="
echo "Starting Crazi Co Flask Application"
echo "=========================================="
echo "PORT: $PORT"
echo "API_BASE: $API_BASE"
echo "PYTHONUNBUFFERED: $PYTHONUNBUFFERED"
echo "=========================================="

# Export PORT for gunicorn
export PORT

# Start gunicorn with logging
exec gunicorn \
    --bind=0.0.0.0:$PORT \
    --timeout=600 \
    --workers=4 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    flask_app:app



