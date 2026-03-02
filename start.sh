#!/bin/bash
set -e

echo "🚀 Starting Bank Fraud Detection Application..."
echo "================================================"

# Start backend in background
echo "Starting backend on port 7777..."
cd /app/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 7777 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
for i in {1..30}; do
  if curl -s http://localhost:7777/health > /dev/null 2>&1; then
    echo "✅ Backend is ready!"
    break
  fi
  echo "  Attempt $i/30... waiting for backend"
  sleep 1
done

# Start frontend in foreground (so container stays alive)
echo "Starting frontend on port 3001..."
cd /app/frontend
exec python3 server.py 3001
