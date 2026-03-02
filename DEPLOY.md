# 🚀 Deploy to Railway (Permanent Public URL)

## Step 1: Sign Up to Railway
Go to **https://railway.app** and sign up with GitHub (takes 30 seconds)

## Step 2: Create New Project
1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Authorize and select this repository

## Step 3: Configure Environment Variables
In Railway dashboard, go to **Variables** and add (optional, if you want):
```
NODE_ENV=production
PYTHON_ENV=production
```

## Step 4: Deploy
Railway automatically detects the Dockerfile and deploys. Takes ~2 minutes.

Once deployed, you'll get a permanent URL like:
```
https://your-project-name.railway.app
```

## Result
✅ Frontend: `https://your-project-name.railway.app`
✅ Backend: `https://your-project-name.railway.app/api/v1`
✅ URL never changes
✅ 24/7 uptime
✅ Free tier includes $5/month credit

---

## Alternative: Deploy to Render

If you prefer **Render.com** instead:
1. Go to https://render.com
2. Click **New +** → **Web Service**
3. Connect GitHub repo
4. Set build command: `npm install && npm run build && cd backend && pip install -r requirements.txt`
5. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 & cd ../frontend && python3 server.py 3001`
6. Deploy

Both give you a permanent public URL!

---

## Quick Check: Is Everything in Git?

For Railway/Render to work, your repo needs to be on GitHub. If not:
```bash
git init
git add .
git commit -m "Add bank fraud detection app"
git remote add origin https://github.com/YOUR_USERNAME/bank-fraud-detection.git
git push -u origin main
```
