#!/bin/sh
set -e

echo "⏳ Waiting for database"
sleep 5

echo "running migrations"
alembic upgrade head

echo "starting celery worker"
celery -A app.core.celery.celery worker --loglevel=info &

echo "starting celery beat"
celery -A app.core.celery.celery beat --loglevel=info &

echo "starting app"
uvicorn app.main:app --host 0.0.0.0 --port 8000