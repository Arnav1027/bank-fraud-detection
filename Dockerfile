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

# Create startup script that works with Railway
WORKDIR /app
RUN echo '#!/bin/bash\nset -e\necho "Starting services..."\ncd /app/backend\npython3 -m uvicorn app.main:app --host 0.0.0.0 --port 7777 2>&1 &\nBACK_PID=$!\nsleep 4\necho "Backend started (PID: $BACK_PID)"\ncd /app/frontend\nexec python3 server.py 3001' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 3001 7777

CMD ["/app/start.sh"]
