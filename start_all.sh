#!/usr/bin/env bash
set -e

echo "Updating repository..."
git pull --ff-only

# Install missing system dependencies
install_packages=()

if ! command -v npm >/dev/null 2>&1; then
  install_packages+=(nodejs npm)
fi

if ! command -v redis-server >/dev/null 2>&1; then
  install_packages+=(redis-server)
fi

if [ ${#install_packages[@]} -gt 0 ]; then
  echo "Installing packages: ${install_packages[*]}"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y "${install_packages[@]}"
  elif command -v brew >/dev/null 2>&1; then
    brew install "${install_packages[@]}"
  else
    echo "Unsupported package manager. Please install ${install_packages[*]} manually." >&2
    exit 1
  fi
fi

# Ensure Redis is running for Celery
if command -v redis-cli >/dev/null 2>&1; then
  if ! redis-cli ping >/dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    # Give Redis a moment to spin up
    sleep 1
  fi
else
  echo "Redis is required but redis-cli is missing even after install attempt." >&2
  exit 1
fi

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
if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed. Please install Node.js and npm to run the frontend." >&2
  exit 1
fi

if [ ! -d web/node_modules ]; then
  echo "Installing frontend dependencies..."
  (cd web && npm install)
fi

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
