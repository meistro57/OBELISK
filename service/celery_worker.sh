#!/usr/bin/env bash
# Start Celery worker for THE AGENCY
exec celery -A service.celery_app.celery_app worker \
  --loglevel=info --concurrency=4 -Q agency
