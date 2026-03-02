# Bank Fraud Detection System

A production-grade, full-stack fraud detection system that uses machine learning to identify fraudulent banking transactions in real-time and batch processing modes. The system combines a powerful Python backend with an interactive React dashboard for comprehensive fraud monitoring and analysis.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## ✨ Features

### Real-Time Fraud Detection
- **Sub-200ms latency** transaction scoring
- **Configurable thresholds** for fraud probability
- **Risk level classification** (low, medium, high)
- **Actionable recommendations** (APPROVE, REVIEW, BLOCK)

### Batch Processing
- CSV upload for bulk transaction analysis
- Concurrent processing with detailed results
- Export fraud scores for further analysis

### Interactive Dashboard
- **Summary cards** showing fraud metrics and KPIs
- **Time-series charts** for trend analysis
- **Transaction table** with filtering and sorting
- **Real-time alerts** for high-risk transactions
- **Model performance metrics** display

### ML Pipeline
- **Multiple algorithms**: Logistic Regression, Random Forest, XGBoost
- **Class imbalance handling**: SMOTE + undersampling
- **Comprehensive evaluation**: Precision, Recall, F1, ROC-AUC, PR-AUC
- **Hyperparameter tuning**: GridSearchCV or Optuna
- **Target metrics**:
  - ✅ Recall ≥ 0.95 (catch fraud)
  - ✅ Precision ≥ 0.80 (minimize false positives)

### Security & Best Practices
- ✅ JWT-based authentication
- ✅ Role-based access control (analyst, admin)
- ✅ Rate limiting on sensitive endpoints
- ✅ Input validation via Pydantic
- ✅ SQL injection prevention (ORM-based)
- ✅ Environment-based configuration
- ✅ Comprehensive logging and monitoring

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **ML/Data Science**: scikit-learn, XGBoost, pandas, NumPy
- **Class Imbalance**: imbalanced-learn (SMOTE)
- **Authentication**: JWT with python-jose
- **Testing**: pytest with 80%+ coverage
- **Code Quality**: Ruff, Black, mypy

### Frontend
- **Framework**: React 18 with TypeScript
- **Charting**: Recharts for interactive visualizations
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Testing**: React Testing Library

### DevOps
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Database Migrations**: Alembic

---

## 🏗 Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (React)"]
        Dashboard["📊 Dashboard"]
        TransactionChecker["🔍 Fraud Checker"]
        AlertPanel["🚨 Alert Panel"]
    end

    subgraph Backend["Backend (FastAPI)"]
        API["API Router"]
        Auth["🔐 Auth Service"]
        FraudDetector["🤖 Fraud Detector"]
        TransactionService["📝 Transaction Service"]
    end

    subgraph ML["ML Pipeline"]
        Preprocess["Preprocessing"]
        FeatureEng["Feature Engineering"]
        Models["Models: LR, RF, XGBoost"]
        Evaluate["Evaluation"]
    end

    subgraph Data["Database"]
        PostgreSQL["PostgreSQL"]
        Models_Storage["Model Artifacts"]
    end

    Frontend -->|REST API| API
    API -->|Auth| Auth
    API -->|Predict| FraudDetector
    API -->|Query/Create| TransactionService
    FraudDetector -->|Load| Models_Storage
    FraudDetector -->|Process| Preprocess
    Preprocess -->|Engineer| FeatureEng
    TransactionService -->|Read/Write| PostgreSQL
    ML -->|Train| Models_Storage
    ML -->|Evaluate| Evaluate
```

### Component Details

#### Backend Architecture
- **API Routes**: Modular endpoints for auth, transactions, analytics
- **Services**: Business logic for fraud detection and transaction management
- **ML Module**: Training, preprocessing, and evaluation pipelines
- **Database**: PostgreSQL with Alembic migrations
- **Security**: JWT authentication and role-based access

#### Data Flow
1. **Real-Time Check**: Transaction → API → Preprocessing → Model → Score → DB
2. **Batch Processing**: CSV Upload → Bulk Preprocessing → Batch Predict → Export
3. **Analytics**: DB Query → Aggregation → Dashboard Visualization

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15+ (for local dev without Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd bank-fraud-detection

# Create environment file
cp .env.example .env

# Start services (includes automatic model training)
docker-compose up --build

# Services will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
```

### Option 2: Local Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example ../.env
# Edit .env with your database credentials

# Train model (generates artifacts)
python train_model.py

# Run tests
pytest tests/ --cov=app --cov-report=term-missing

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
# Opens at http://localhost:3000
```

#### Database Setup
```bash
# Create PostgreSQL database
createdb -U postgres fraud_db
# Set credentials in .env
```

---

## 📖 Setup Instructions

### 1. Environment Configuration

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://fraud_user:fraud_password@postgres:5432/fraud_db

# API
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML
FRAUD_THRESHOLD=0.5  # Configurable fraud score threshold

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

### 2. Database Migrations

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 3. Model Training

```bash
cd backend

# Train and save models
python train_model.py

# Output:
# - app/ml/models/best_model.joblib
# - app/ml/models/preprocessor.joblib
# - plots/roc_curve.png
# - plots/pr_curve.png
# - plots/confusion_matrix.png
```

### 4. Create Admin User (Optional)

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123",
    "full_name": "Admin User"
  }'
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication Endpoints

#### Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "User Name"
}

Response 200:
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "User Name",
    "role": "analyst"
  }
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Transaction Endpoints

#### Real-Time Fraud Check
```http
POST /transactions/check
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": 1,
  "amount": 150.50,
  "merchant_id": "MERCH_001",
  "merchant_category": "grocery",
  "transaction_location": "NYC",
  "transaction_timestamp": "2024-02-24T10:30:00Z"
}

Response 200:
{
  "transaction_id": 1,
  "fraud_score": 0.12,
  "is_fraud": false,
  "risk_level": "low",
  "recommendation": "APPROVE",
  "processing_time_ms": 45.23
}
```

#### List Transactions
```http
GET /transactions/?skip=0&limit=20&is_fraud=false&min_amount=100&max_amount=500
Authorization: Bearer {token}

Response 200:
{
  "total": 245,
  "page": 1,
  "page_size": 20,
  "items": [...]
}
```

#### Batch Fraud Check
```http
POST /transactions/batch
Authorization: Bearer {token}
Content-Type: multipart/form-data

[CSV file with transactions]

Response 200:
{
  "status": "success",
  "records_processed": 1000,
  "fraud_count": 23,
  "csv_data": "..."
}
```

### Analytics Endpoints

#### Summary Statistics
```http
GET /analytics/summary?days=7
Authorization: Bearer {token}

Response 200:
{
  "summary": {
    "total_transactions": 5000,
    "flagged_transactions": 85,
    "fraud_rate": 0.017,
    "total_amount_at_risk": 45230.50,
    "avg_fraud_score": 0.23,
    "high_risk_count": 12
  },
  "top_alerts": [...],
  "daily_fraud_counts": {"2024-02-24": 15, ...}
}
```

#### Recent Alerts
```http
GET /analytics/alerts?limit=20&min_fraud_score=0.8
Authorization: Bearer {token}
```

#### Model Metrics
```http
GET /analytics/metrics
Authorization: Bearer {token}

Response 200:
{
  "accuracy": 0.95,
  "precision": 0.85,
  "recall": 0.98,
  "f1_score": 0.91,
  "roc_auc": 0.96,
  "pr_auc": 0.88,
  "confusion_matrix": {...},
  "model_version": "1.0.0"
}
```

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧠 Machine Learning Pipeline

### Feature Engineering

The system extracts comprehensive features from transaction data:

#### Time-Based Features
- Hour of day (0-23)
- Day of week (0-6)
- Weekend flag (0/1)
- Month (1-12)

#### Amount Features
- Raw amount
- Log-scaled amount
- Squared amount
- Normalized amount (z-score)

#### Merchant Features
- Merchant risk score (based on category)
- Merchant ID encoding
- Category encoding

#### User Features
- Transaction count per user
- Location history
- Temporal patterns

### Models Trained

#### 1. Logistic Regression (Baseline)
- Fast inference
- Interpretable coefficients
- Handles class imbalance with `class_weight='balanced'`

#### 2. Random Forest
- Captures non-linear patterns
- Feature importance ranking
- Robust to outliers

#### 3. XGBoost
- State-of-the-art performance
- Handles class imbalance natively
- Fast gradient boosting

### Class Imbalance Handling

```python
# SMOTE oversampling + Random undersampling
imblearn.Pipeline([
    ('smote', SMOTE(random_state=42)),
    ('undersampler', RandomUnderSampler(random_state=42)),
    ('classifier', model)
])
```

### Evaluation Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| **Recall** | ≥ 0.95 | Catch fraud (minimize false negatives) |
| **Precision** | ≥ 0.80 | Minimize false positives |
| **F1-Score** | ≥ 0.88 | Balanced performance |
| **ROC-AUC** | ≥ 0.95 | Overall discrimination ability |
| **PR-AUC** | ≥ 0.85 | Performance on imbalanced data |

### Training Script

```bash
python train_model.py

# Generates:
# ✓ Best trained model (joblib format)
# ✓ Preprocessor with fitted scalers
# ✓ Evaluation plots (ROC, PR, Confusion Matrix)
# ✓ Detailed metrics report
```

### Model Retraining

```bash
# Retrain with new data
python train_model.py

# Update in production
docker-compose restart backend
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/test_api/test_integration.py -v

# Run with markers
pytest -m "not slow" tests/
```

### Test Structure
- **test_ml/**: Preprocessing and feature engineering tests
- **test_api/**: API integration and endpoint tests
- **test_services/**: Business logic service tests

### Coverage Target
- **Minimum**: 80%
- **Target**: >90%
- **View report**: Open `htmlcov/index.html` after coverage run

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific component
npm test -- Dashboard.test.tsx
```

---

## 🐳 Deployment

### Using Docker Compose

```bash
# Production build
docker-compose -f docker-compose.yml up --build

# With custom environment
FRAUD_THRESHOLD=0.6 docker-compose up
```

### Environment Considerations

```env
# Production Settings
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=postgresql://user:pass@prod-db:5432/fraud_db
CORS_ORIGINS=https://yourdomain.com

# ML Settings
FRAUD_THRESHOLD=0.5
MODEL_PATH=/app/models/production_model.joblib
```

### Database Backup

```bash
# Backup
pg_dump -U fraud_user -d fraud_db > backup.sql

# Restore
psql -U fraud_user -d fraud_db < backup.sql
```

### Monitoring

- **API Health**: `GET /health`
- **Database**: Check PostgreSQL logs
- **ML Model**: Monitor fraud_score distributions
- **Performance**: Track API response times

---

## 📊 Dashboard Screenshots

### Summary View
- KPI cards showing fraud metrics
- Daily fraud trend chart
- Transaction distribution pie chart
- Recent alerts table

### Transaction Checker
- Real-time fraud scoring interface
- Risk level visualization
- Recommendation display
- Processing time metrics

---

## 🔐 Security Considerations

1. **Secrets Management**: Use environment variables, never hardcode secrets
2. **Database**: PostgreSQL with encrypted passwords, regular backups
3. **API**: Rate limiting, CORS configuration, input validation
4. **Authentication**: JWT tokens with 30-minute expiration
5. **Logging**: Structured JSON logs without sensitive data
6. **Monitoring**: Alert on suspicious patterns

---

## 🐛 Troubleshooting

### Common Issues

**1. Model Not Loading**
```bash
# Check if model files exist
ls app/ml/models/
# Retrain if missing
python train_model.py
```

**2. Database Connection Error**
```bash
# Check PostgreSQL is running
psql -U fraud_user -d fraud_db -c "SELECT 1;"
# Verify DATABASE_URL in .env
```

**3. API Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill and restart
```

**4. Slow Model Inference**
```bash
# Check preprocessing cache
# Verify model version
curl http://localhost:8000/api/v1/transactions/check -X GET
```

---

## 📈 Performance Characteristics

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Real-time fraud check | <200ms | 100+ req/s |
| Batch processing (1000 txns) | <5s | 200+ txns/s |
| Dashboard load | <1s | 50+ users |
| Model inference (single) | 10-50ms | - |

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Run tests: `pytest` and `npm test`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include logs and reproduction steps

---

## 🎯 Roadmap

- [ ] Deep learning models (LSTM, Autoencoder)
- [ ] Real-time feature store integration
- [ ] Explainability (SHAP values)
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Webhook notifications
- [ ] Advanced analytics dashboards
- [ ] A/B testing framework

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [scikit-learn](https://scikit-learn.org/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

**Built with ❤️ for fraud detection excellence.**
