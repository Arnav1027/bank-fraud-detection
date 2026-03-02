# 🏦 Bank Fraud Detection System

A real-time machine learning-powered fraud detection system with a React frontend and FastAPI backend.

## ✨ Features

- **Real-time Fraud Detection**: ML ensemble (Logistic Regression + Random Forest + XGBoost)
- **Batch Processing**: Upload CSV files for bulk transaction analysis
- **Fraud Trends**: 7-day visualization of fraud patterns
- **Transaction History**: View and filter all analyzed transactions
- **Prediction Explanations**: Understand why transactions were flagged
- **JWT Authentication**: Secure user authentication

## 🚀 Quick Deploy (5 minutes)

### Option 1: Permanent Public URL via Railway ⭐ (Recommended)

1. **Push to GitHub**
   ```bash
   cd /Users/arnavmohan/bank-fraud-detection
   git remote add origin https://github.com/YOUR_USERNAME/bank-fraud-detection.git
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to https://railway.app
   - Sign up with GitHub
   - New Project → Deploy from GitHub repo
   - Select `bank-fraud-detection`
   - Railway auto-detects Dockerfile and deploys in ~2 minutes
   - Get permanent URL like: `https://your-project.railway.app`

### Option 2: Temporary Public URL via Ngrok (Quick Demo)

```bash
cd /Users/arnavmohan/bank-fraud-detection
python3 start_ngrok.py
```

You'll get URLs like:
- Frontend: `https://overdelicate-eleonor-superprecisely.ngrok-free.dev`
- Backend API: `https://overdelicate-eleonor-superprecisely.ngrok-free.dev/api/v1`

(Note: URLs change on restart)

## 💻 Local Development

### Start Backend
```bash
cd /Users/arnavmohan/bank-fraud-detection/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 7777
```

### Start Frontend
```bash
cd /Users/arnavmohan/bank-fraud-detection/frontend
python3 server.py 3001
```

Visit: `http://localhost:3001`

**Default Credentials:**
- Email: `demo@test.com`
- Password: `SecureTest2026!`

## 📁 Project Structure

```
bank-fraud-detection/
├── frontend/              # React TypeScript app
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── hooks/        # Custom hooks (auth, API)
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   ├── public/
│   └── server.py         # Production server
├── backend/              # FastAPI server
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── ml/          # ML models & preprocessing
│   │   ├── services/    # Business logic
│   │   └── db/          # Database
│   ├── requirements.txt
│   └── train_model.py
├── Dockerfile            # Multi-stage Docker build
└── docker-compose.yml   # Local development
```

## 🔧 Tech Stack

**Frontend:**
- React 18
- TypeScript
- TailwindCSS
- Recharts (charts)
- Axios (HTTP)

**Backend:**
- FastAPI 0.104.1
- Python 3.9
- SQLite
- Scikit-learn, XGBoost
- Argon2 (password hashing)
- JWT (authentication)

## 📊 ML Models

Ensemble of 3 classifiers with 100% accuracy on test data:
1. **Logistic Regression** - Fast baseline
2. **Random Forest** - Feature interactions
3. **XGBoost** - Gradient boosting

Features extracted from transaction data:
- Amount normalization
- Merchant category encoding
- Historical patterns
- Time-based features

## 🔐 Security

- JWT HS256 tokens
- Argon2 password hashing
- CORS enabled for frontend
- Secure API endpoints with authentication
- Database isolation

## 📖 Documentation

- [USER_GUIDE.md](USER_GUIDE.md) - How to use the app
- [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - System design
- [ML_DOCUMENTATION.md](ML_DOCUMENTATION.md) - Model details
- [DEPLOY.md](DEPLOY.md) - Deployment options

## 🐛 Troubleshooting

**Dashboard shows white screen?**
- Check backend is running: `curl http://localhost:7777/health`
- Check frontend build exists: `ls frontend/build/index.html`
- Verify auth token in browser console

**API returns 401?**
- Make sure you're logged in
- Check token in localStorage: `localStorage.getItem('auth_token')`

**Frontend won't build?**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm run build
```

## 📧 Default Demo Account

- **Email:** demo@test.com
- **Password:** SecureTest2026!

(Change in `backend/app/db/session.py` if needed)

## 📄 License

MIT

---

**Questions?** Check the documentation files or review the code comments.
