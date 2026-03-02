#!/bin/bash
# This script pushes your code to GitHub and deploys to Railway

echo "=========================================="
echo "🚀 Deploying Bank Fraud Detection App"
echo "=========================================="

# Step 1: Create GitHub repo (manual)
echo ""
echo "Step 1️⃣  CREATE GITHUB REPO:"
echo "  1. Go to https://github.com/new"
echo "  2. Create repo named: bank-fraud-detection"
echo "  3. Do NOT initialize with README (we already have one)"
echo "  4. Click 'Create repository'"
echo ""
read -p "Press enter when repo is created..."

# Step 2: Add remote and push
echo ""
echo "Step 2️⃣  PUSHING CODE TO GITHUB..."
echo "  Enter your GitHub username:"
read github_user

git remote add origin https://github.com/$github_user/bank-fraud-detection.git
git branch -M main
git push -u origin main

echo "✅ Code pushed to GitHub!"

# Step 3: Deploy to Railway
echo ""
echo "=========================================="
echo "Step 3️⃣  DEPLOY TO RAILWAY:"
echo "=========================================="
echo ""
echo "  1. Go to https://railway.app"
echo "  2. Sign up with GitHub (takes 30 seconds)"
echo "  3. Click 'New Project' → 'Deploy from GitHub repo'"
echo "  4. Select 'bank-fraud-detection'"
echo "  5. Railway auto-detects Dockerfile and deploys"
echo "  6. Wait 2-3 minutes"
echo ""
echo "You'll get a permanent URL! ✨"
echo ""
echo "=========================================="
