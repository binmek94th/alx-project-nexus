#!/bin/bash

# Wait for Postgres to be ready
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Postgres is ready"

# Run Django setup commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Start ASGI server
exec uvicorn alx_project_nexus.asgi:application --host 0.0.0.0 --port 8000
