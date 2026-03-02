FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY frontend/public ./public
COPY frontend/src ./src
RUN npm run build

FROM python:3.9-slim

WORKDIR /app

# Install Node for any runtime needs
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend /app/backend
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build /app/frontend/build
COPY frontend/server.py /app/frontend/server.py

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 7777 &\n\
sleep 3 && cd /app/frontend && python3 server.py 3001\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 3001 7777

CMD ["/app/start.sh"]
