#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn

# Django commands
python manage.py collectstatic --no-input
python manage.py migrate