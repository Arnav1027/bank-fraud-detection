#!/bin/bash
set -e

echo "🚀 Starting Bank Fraud Detection Application..."
echo "================================================"

# Use PORT environment variable from Railway, default to 8000
PORT=${PORT:-8000}
BACKEND_PORT=$((PORT + 1))  # Backend on PORT+1 (e.g., 8001)

echo "Frontend will run on port: $PORT"
echo "Backend will run on port: $BACKEND_PORT"

# Start backend in background
echo "Starting backend..."
cd /app/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
for i in {1..30}; do
  if curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is ready!"
    break
  fi
  echo "  Attempt $i/30... waiting for backend"
  sleep 1
done

# Start frontend in foreground (so container stays alive)
echo "Starting frontend..."
cd /app/frontend
exec python3 server.py $PORT
