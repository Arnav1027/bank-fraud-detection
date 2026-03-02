# Quick Start Guide

## 30-Second Setup (Docker)

```bash
# Clone and navigate
git clone <repo>
cd bank-fraud-detection

# Setup environment
cp .env.example .env

# Start everything
docker-compose up --build

# Wait for services... (~2-3 minutes for first run)
```

**Done!** Your system is ready:
- 🌐 Frontend: http://localhost:3000
- 🔌 API: http://localhost:8000
- 📚 Docs: http://localhost:8000/docs

### First Login

Create account or use test credentials:
```
Email: demo@example.com
Password: Demo123456
```

---

## Local Development (5 minutes)

### Prerequisites
- Python 3.11
- Node.js 18
- PostgreSQL 15

### Backend

```bash
cd backend

# Virtual environment
python -m venv venv
source venv/bin/activate

# Install & train
pip install -r requirements.txt
python train_model.py

# Test
pytest tests/

# Run
uvicorn app.main:app --reload
```

Open: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install & run
npm install
npm start
```

Open: http://localhost:3000

---

## Key Commands

### Training Models
```bash
python train_model.py
# Output: app/ml/models/best_model.joblib
```

### Running Tests
```bash
# Backend
pytest tests/ --cov=app

# Frontend
npm test
```

### Database
```bash
# Migrations
alembic upgrade head
alembic downgrade -1
```

### Docker
```bash
# Logs
docker-compose logs -f backend

# Rebuild
docker-compose up --build

# Clean
docker-compose down -v
```

---

## API Examples

### Login & Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Real-Time Fraud Check
```bash
TOKEN="<your-token>"

curl -X POST http://localhost:8000/api/v1/transactions/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "amount": 150.50,
    "merchant_id": "MERCH_001",
    "merchant_category": "grocery",
    "transaction_location": "NYC",
    "transaction_timestamp": "2024-02-24T10:30:00Z"
  }'
```

### Get Dashboard Data
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

### Interactive Docs
Open: http://localhost:8000/docs (Swagger UI)

---

## Project Structure

```
bank-fraud-detection/
├── backend/                 # Python FastAPI
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── api/routes/     # Endpoints
│   │   ├── ml/             # ML pipeline
│   │   ├── models.py       # DB models
│   │   └── services/       # Business logic
│   ├── train_model.py      # Training script
│   └── requirements.txt
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── types/          # TypeScript types
│   │   └── services/       # API client
│   └── package.json
├── docker-compose.yml      # Compose config
└── README.md              # Full documentation
```

---

## Common Issues

### Port Already in Use
```bash
# Kill process on port
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL
psql -U fraud_user -d fraud_db -c "SELECT 1;"

# Or use Docker
docker-compose logs postgres
```

### Model Not Loading
```bash
# Retrain
python train_model.py

# Verify
ls app/ml/models/
```

---

## Next Steps

1. **Create Account**: Sign up in UI (http://localhost:3000)
2. **Check Transaction**: Use the fraud checker
3. **View Dashboard**: Monitor analytics
4. **Upload CSV**: Test batch processing
5. **Read Full Docs**: See README.md

---

## Support

- Full docs: [README.md](README.md)
- ML docs: [ML_DOCUMENTATION.md](ML_DOCUMENTATION.md)
- API docs: http://localhost:8000/docs
- Issues: Check GitHub Issues

---

**Happy fraud detection! 🚀**
