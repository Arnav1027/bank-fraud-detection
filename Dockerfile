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
ENV REACT_APP_API_URL=/api/v1
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Copy entire project first
COPY . /app/

# Install backend dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Prepare frontend
WORKDIR /app/frontend
COPY --from=frontend-builder /app/frontend/build ./build

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000 8001

WORKDIR /app
CMD ["/app/start.sh"]
