#!/bin/bash

# Activate your virtual environment (if necessary)
# source /path/to/venv/bin/activate

# Set the necessary environment variables
export APP_SETTINGS=config.DevelopmentConfig
export FLASK_APP=app.py

# Start gunicorn
exec gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --workers 10 \
    --log-level=debug \
    --access-logfile '-' \
    --error-logfile '-'
