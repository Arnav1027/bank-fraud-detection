FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps 2>&1 | grep -v "warn"
COPY frontend/public ./public
COPY frontend/src ./src
COPY frontend/tsconfig.json ./
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./
COPY frontend/.prettierrc ./
RUN npm run build

FROM python:3.9-slim

WORKDIR /app

# Copy entire project first
COPY . /app/

# Install backend dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Prepare frontend
WORKDIR /app/frontend
COPY --from=frontend-builder /app/frontend/build ./build

# Create startup script
WORKDIR /app
RUN echo '#!/bin/bash\nset -e\necho "Starting Bank Fraud Detection..."\ncd /app/backend\npython3 -m uvicorn app.main:app --host 0.0.0.0 --port 7777 &\nBACKEND_PID=$!\necho "Backend started (PID: $BACKEND_PID)"\nsleep 3\ncd /app/frontend\npython3 server.py 3001\nwait $BACKEND_PID' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 3001 7777

CMD ["/app/start.sh"]
