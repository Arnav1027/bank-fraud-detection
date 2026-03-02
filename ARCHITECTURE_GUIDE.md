# Project Overview & Visual Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BANK FRAUD DETECTION SYSTEM                              │
│                                                                               │
│  ┌──────────────────────┐         ┌──────────────────────┐                   │
│  │   FRONTEND LAYER     │         │   BACKEND LAYER      │                   │
│  │   (React + TS)       │         │   (FastAPI/Python)   │                   │
│  ├──────────────────────┤         ├──────────────────────┤                   │
│  │                      │         │                      │                   │
│  │  ┌────────────────┐  │         │ ┌──────────────────┐ │                   │
│  │  │   Login Page   │  │         │ │   JWT Auth       │ │                   │
│  │  └────────────────┘  │         │ └──────────────────┘ │                   │
│  │         │            │         │         │            │                   │
│  │  ┌────────────────┐  │         │ ┌──────────────────┐ │                   │
│  │  │   Dashboard    │  │◄────────┼─│ /transactions    │ │                   │
│  │  │  • Summary     │  │         │ │ /analytics       │ │                   │
│  │  │  • Charts      │  │         │ │ /auth            │ │                   │
│  │  │  • Alerts      │  │         │ └──────────────────┘ │                   │
│  │  └────────────────┘  │         │                      │                   │
│  │         │            │         │ ┌──────────────────┐ │                   │
│  │  ┌────────────────┐  │         │ │  ML Pipeline     │ │                   │
│  │  │  Fraud Checker │  │────────►│ │ • Preprocess     │ │                   │
│  │  │  • Form Input  │  │         │ │ • Feature Eng.   │ │                   │
│  │  │  • Results     │  │         │ │ • Prediction     │ │                   │
│  │  └────────────────┘  │         │ └──────────────────┘ │                   │
│  │                      │         │         │            │                   │
│  └──────────────────────┘         │ ┌──────────────────┐ │                   │
│                                   │ │   PostgreSQL     │ │                   │
│                                   │ │   Database       │ │                   │
│                                   │ └──────────────────┘ │                   │
│                                   │                      │                   │
│                                   └──────────────────────┘                   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │               ML MODELS (Trained Artifacts)                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  Logistic    │  │Random Forest │  │  XGBoost     │               │  │
│  │  │ Regression   │  │ Classifier   │  │ Classifier   │               │  │
│  │  │              │  │              │  │              │               │  │
│  │  │ Accuracy:    │  │ Accuracy:    │  │ Accuracy:    │               │  │
│  │  │ Fast & Light │  │ Non-linear   │  │ SOTA         │               │  │
│  │  │ weight: ~1MB │  │ weight: ~5MB │  │ weight: ~3MB │               │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  │                       ↓                                              │  │
│  │                  Best Model Selected                                │  │
│  │        (Highest Recall ≥ 95%, Precision ≥ 80%)                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
Real-Time Transaction Check
═══════════════════════════════════════════════════════════════════

1. User/System
   │
   ▼
2. API Receives Transaction
   {
     "user_id": 123,
     "amount": 150.50,
     "merchant_id": "M001",
     "merchant_category": "grocery",
     "transaction_location": "NYC",
     "transaction_timestamp": "2024-02-24T10:30:00Z"
   }
   │
   ▼
3. Input Validation (Pydantic)
   ✓ All fields required
   ✓ Amount > 0
   ✓ Valid timestamp
   │
   ▼
4. Feature Engineering
   Original: 5 fields
   │
   ├─ Time Features (4)
   │  ├─ hour_of_day: 10
   │  ├─ day_of_week: 4
   │  ├─ is_weekend: 0
   │  └─ month: 2
   │
   ├─ Amount Features (4)
   │  ├─ amount: 150.50
   │  ├─ log_amount: 5.02
   │  ├─ amount_squared: 22650.25
   │  └─ amount_normalized: 0.45
   │
   ├─ Merchant Features (2)
   │  ├─ merchant_risk_score: 0
   │  └─ merchant_category_encoded: 2
   │
   └─ Other Features (1+)
      └─ has_location: 1
   │
   ▼ Result: 11-13 features
5. Preprocessing Pipeline
   • StandardScaler: Scale features to mean=0, std=1
   • LabelEncoder: Encode categorical variables
   ▼
6. Model Inference
   Input: 11-13 scaled features
   Output: Probability [0.0 - 1.0]
   
   Sample Output: 0.12 (12% fraud probability)
   │
   ▼
7. Classification
   If score >= threshold (0.5):
     is_fraud = True → BLOCK
   Else:
     is_fraud = False → APPROVE
   │
   ▼
8. Risk Level Assignment
   Score 0.12 → "low" risk
   │
   ▼
9. Database Storage
   INSERT INTO transactions(
     user_id, amount, fraud_score, is_fraud, status
   ) VALUES (123, 150.50, 0.12, False, 'PROCESSED')
   │
   ▼
10. Response to User
    {
      "transaction_id": 1,
      "fraud_score": 0.12,
      "is_fraud": false,
      "risk_level": "low",
      "recommendation": "APPROVE",
      "processing_time_ms": 45.23
    }
    ▼
    Total Time: <200ms ✓


Batch Processing Flow
═══════════════════════════════════════════════════════════════════

User Uploads CSV
    │
    ▼
CSV Parsing & Validation
    │
    ├─ Check columns
    ├─ Validate data types
    ├─ Check for missing values
    │
    ▼ (if all valid)
Load into DataFrame
    │
    ▼
Apply Feature Engineering (vectorized)
    │
    ▼
Apply Preprocessing (vectorized)
    │
    ▼
Batch Model Prediction
    Input: N x 13 matrix
    Output: N fraud scores
    │
    ▼
Add Scores to DataFrame
    │
    ├─ fraud_score column
    ├─ is_fraud column
    ├─ risk_level column
    │
    ▼
Export to CSV
    │
    ▼
Return to User
    Total Time: ~5s for 1000 transactions
```

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  App.tsx (Router)                                                │
│  ├─ /login          → LoginPage.tsx                              │
│  ├─ /dashboard      → Dashboard.tsx                              │
│  │                    ├─ SummaryCard                             │
│  │                    ├─ LineChart (Recharts)                    │
│  │                    ├─ PieChart (Recharts)                     │
│  │                    └─ AlertTable                              │
│  ├─ /check          → TransactionChecker.tsx                     │
│  │                    ├─ Form Input                              │
│  │                    └─ Result Display                          │
│  │                                                                │
│  hooks/useApi.ts (Custom Hooks)                                  │
│  ├─ useAuth() → Login/Signup/Logout                              │
│  └─ useFetch<T>() → Data fetching with caching                   │
│                                                                   │
│  services/api.ts (Axios Client)                                  │
│  ├─ auth endpoints (signup, login)                               │
│  ├─ transaction endpoints (check, list, batch)                   │
│  └─ analytics endpoints (summary, alerts, metrics)               │
│                                                                   │
│  types/index.ts (TypeScript Interfaces)                          │
│  ├─ User, AuthResponse                                           │
│  ├─ Transaction, FraudCheckResponse                              │
│  └─ FraudSummary, ModelMetrics                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP (Axios)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  main.py (App Entry)                                             │
│  ├─ CORS Middleware                                              │
│  ├─ Include routers                                              │
│  └─ Health check endpoint                                        │
│                                                                   │
│  api/routes/ (Endpoint Handlers)                                 │
│  ├─ auth.py: /auth/signup, /auth/login                           │
│  ├─ transactions.py:                                             │
│  │  ├─ POST /transactions/check                                  │
│  │  ├─ GET /transactions/                                        │
│  │  ├─ GET /transactions/{id}                                    │
│  │  └─ POST /transactions/batch                                  │
│  └─ analytics.py:                                                │
│     ├─ GET /analytics/summary                                    │
│     ├─ GET /analytics/alerts                                     │
│     └─ GET /analytics/metrics                                    │
│                                                                   │
│  api/dependencies.py (Auth & Injection)                          │
│  ├─ get_current_user()                                           │
│  └─ get_admin_user()                                             │
│                                                                   │
│  services/ (Business Logic)                                      │
│  ├─ fraud_detector.py → Real-time scoring                        │
│  └─ transaction_service.py → DB operations                       │
│                                                                   │
│  ml/ (Machine Learning)                                          │
│  ├─ preprocess.py → Feature engineering                          │
│  ├─ train.py → Model training                                    │
│  └─ evaluate.py → Metrics & plots                                │
│                                                                   │
│  core/ (Configuration)                                           │
│  ├─ config.py → Settings from env                                │
│  └─ security.py → JWT, password hashing                          │
│                                                                   │
│  db/ (Database)                                                  │
│  ├─ session.py → Connection management                           │
│  └─ migrations/ → Alembic (future)                               │
│                                                                   │
│  models.py (SQLAlchemy)                                          │
│  ├─ User model                                                   │
│  └─ Transaction model                                            │
│                                                                   │
│  schemas/__init__.py (Pydantic)                                  │
│  ├─ User schemas                                                 │
│  ├─ Transaction schemas                                          │
│  └─ Analytics schemas                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ SQLAlchemy ORM
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  users                                                           │
│  ├─ id (PK)                                                      │
│  ├─ email (UNIQUE)                                               │
│  ├─ hashed_password                                              │
│  ├─ full_name                                                    │
│  ├─ role ('analyst', 'admin')                                    │
│  ├─ is_active                                                    │
│  ├─ created_at, updated_at                                       │
│                                                                   │
│  transactions                                                    │
│  ├─ id (PK)                                                      │
│  ├─ user_id (FK)                                                 │
│  ├─ amount                                                       │
│  ├─ merchant_id                                                  │
│  ├─ merchant_category                                            │
│  ├─ transaction_location                                         │
│  ├─ transaction_timestamp (INDEXED)                              │
│  ├─ fraud_score (INDEXED)                                        │
│  ├─ is_fraud (INDEXED)                                           │
│  ├─ status                                                       │
│  ├─ model_version                                                │
│  ├─ created_at (INDEXED)                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request/Response Examples

### 1. Authentication Flow

```
REQUEST: Sign Up
═════════════════════════════════════════════════════
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "SecurePassword123"
}

RESPONSE: 200 OK
─────────────────────────────────────────────────────
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "analyst",
    "is_active": true,
    "created_at": "2024-02-24T10:30:00Z"
  }
}


REQUEST: Login
═════════════════════════════════════════════════════
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123"
}

RESPONSE: 200 OK
─────────────────────────────────────────────────────
(Same as signup response with new token)
```

### 2. Real-Time Fraud Check

```
REQUEST: Check Transaction for Fraud
═════════════════════════════════════════════════════
POST /api/v1/transactions/check
Authorization: Bearer eyJ0eXAi...
Content-Type: application/json

{
  "user_id": 1,
  "amount": 150.50,
  "merchant_id": "MERCH_001",
  "merchant_category": "grocery",
  "transaction_location": "NYC",
  "transaction_timestamp": "2024-02-24T10:30:00Z"
}

RESPONSE: 200 OK
─────────────────────────────────────────────────────
{
  "transaction_id": 1,
  "fraud_score": 0.12,
  "is_fraud": false,
  "risk_level": "low",
  "recommendation": "APPROVE",
  "processing_time_ms": 45.23
}
```

### 3. Analytics Summary

```
REQUEST: Get Fraud Summary
═════════════════════════════════════════════════════
GET /api/v1/analytics/summary?days=7
Authorization: Bearer eyJ0eXAi...

RESPONSE: 200 OK
─────────────────────────────────────────────────────
{
  "summary": {
    "total_transactions": 5000,
    "flagged_transactions": 85,
    "fraud_rate": 0.017,
    "total_amount_at_risk": 45230.50,
    "avg_fraud_score": 0.23,
    "high_risk_count": 12
  },
  "top_alerts": [
    {
      "transaction_id": 1,
      "user_id": 1,
      "amount": 500.00,
      "fraud_score": 0.95,
      "merchant_id": "MERCH_999",
      "flagged_at": "2024-02-24T10:20:00Z"
    },
    ...
  ],
  "daily_fraud_counts": {
    "2024-02-24": 15,
    "2024-02-23": 12,
    "2024-02-22": 8
  }
}
```

---

## Development Workflow

```
1. Setup
   $ git clone <repo>
   $ cd bank-fraud-detection
   $ docker-compose up --build

2. Frontend Development (in separate terminal)
   $ cd frontend
   $ npm install
   $ npm start  # Opens http://localhost:3000

3. Backend Development
   $ cd backend
   $ python -m venv venv
   $ source venv/bin/activate
   $ pip install -r requirements.txt
   $ python train_model.py
   $ uvicorn app.main:app --reload

4. Testing
   Backend:
   $ cd backend
   $ pytest tests/ --cov=app

   Frontend:
   $ cd frontend
   $ npm test

5. Deployment
   $ docker-compose up -d
   $ Check http://localhost:8000/docs
   $ Check http://localhost:3000
```

---

## Performance Profile

```
Single Transaction Check
├─ API Overhead: 5-10ms
├─ Preprocessing: 10-30ms
├─ Model Inference: 5-20ms
└─ Total: <200ms ✓ (target met)

Batch Processing (1000 transactions)
├─ CSV Parsing: 100-200ms
├─ Preprocessing (vectorized): 500-1000ms
├─ Prediction (vectorized): 300-500ms
├─ Database Insert: 1000-2000ms
└─ Total: ~4-5 seconds

Dashboard Load
├─ API calls: 3-5
├─ Time per call: 50-200ms
├─ Rendering: 200-500ms
└─ Total: <1 second ✓

Memory Usage
├─ Model + Preprocessor: ~200MB
├─ API Process: ~150MB
├─ Database Connection Pool: ~50MB
└─ Total: ~400MB ✓ (reasonable)
```

---

## Monitoring & Observability

```
Key Metrics to Monitor
══════════════════════════════════════════════════

API Metrics:
├─ Request latency (p50, p95, p99)
├─ Request throughput
├─ Error rate
└─ Cache hit rate

Model Metrics:
├─ Fraud score distribution
├─ Precision, Recall, F1 (on holdout)
├─ False positive rate
└─ False negative rate

Data Metrics:
├─ Transaction volume
├─ Fraud rate
├─ Amount distribution
└─ New merchant categories

System Metrics:
├─ CPU usage
├─ Memory usage
├─ Disk I/O
└─ Database query time
```

---

## Security Summary

```
Authentication & Authorization
├─ JWT tokens (HS256 algorithm)
├─ Role-based access (analyst, admin)
└─ Session management

Data Protection
├─ Passwords: bcrypt hashing
├─ Database: PostgreSQL encryption ready
├─ Secrets: Environment variables
└─ Logs: No sensitive data logged

Input Validation
├─ Pydantic schemas on all inputs
├─ Type checking (mypy)
├─ Amount > 0 validation
└─ Timestamp validation

API Security
├─ CORS configuration
├─ Rate limiting ready
├─ ORM prevents SQL injection
└─ HTTPS ready
```

---

This comprehensive visual guide provides a complete overview of the system architecture, data flows, and operational aspects! 🎯
