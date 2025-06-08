#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Django commands
if [ "$DATABASE_URL" != "" ]; then
    echo "Running migrations..."
    python manage.py migrate
else
    echo "No DATABASE_URL, skipping migrations"
fi

python manage.py collectstatic --no-input

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t mohinska/plidno:latest --push .