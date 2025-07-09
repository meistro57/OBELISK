#!/usr/bin/env bash
set -e

# Activate venv if exists
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

echo "Starting FastAPI..."
uvicorn service.api:app --reload &
API_PID=$!

echo "Starting Celery worker..."
chmod +x service/celery_worker.sh
service/celery_worker.sh &
WORKER_PID=$!

echo "Starting Celery Beat..."
celery -A service.celery_app.celery_app beat --loglevel=info &
BEAT_PID=$!

echo "Starting Frontend..."
cd web && npm run dev &
FRONTEND_PID=$!

echo "All services started. PIDs: API=$API_PID, WORKER=$WORKER_PID, BEAT=$BEAT_PID, FRONTEND=$FRONTEND_PID"
# Open browser to the dashboard (if available)
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:5174 &
elif command -v open >/dev/null 2>&1; then
  open http://localhost:5174 &
fi

wait
