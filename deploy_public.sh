#!/bin/bash

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🚀 Deploying Bank Fraud Detection to Public URL          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Verify git is initialized
echo "Step 1️⃣  Checking git repository..."
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Initializing now..."
    git init
    git config user.name "Arnav"
    git config user.email "arnav@example.com"
    git add -A
    git commit -m "Initial commit: Bank Fraud Detection app"
else
    echo "✅ Git repository ready"
fi

# Step 2: Get GitHub username
echo ""
echo "Step 2️⃣  GitHub Setup"
read -p "Enter your GitHub username: " github_user

if [ -z "$github_user" ]; then
    echo "❌ GitHub username required. Exiting."
    exit 1
fi

# Step 3: Push to GitHub
echo ""
echo "Step 3️⃣  Pushing code to GitHub..."
echo "   Repository: https://github.com/$github_user/bank-fraud-detection"
echo ""

# Check if remote exists
if git remote | grep -q origin; then
    echo "Updating existing remote..."
    git remote set-url origin https://github.com/$github_user/bank-fraud-detection.git
else
    echo "Adding new remote..."
    git remote add origin https://github.com/$github_user/bank-fraud-detection.git
fi

git branch -M main

echo ""
echo "⚠️  You'll be prompted to authenticate with GitHub"
echo "   Use a GitHub Personal Access Token (https://github.com/settings/tokens/new)"
echo "   Scopes: Select 'repo' only"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pushed to GitHub successfully!"
else
    echo "❌ Failed to push to GitHub. Check your credentials and try again."
    exit 1
fi

# Step 4: Deploy to Railway
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   ✅ GitHub setup complete!                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Step 4️⃣  Deploy to Railway"
echo ""
echo "   1. Go to: https://railway.app"
echo "   2. Sign up with GitHub (authorize the app)"
echo "   3. Click 'New Project' (top right)"
echo "   4. Select 'Deploy from GitHub repo'"
echo "   5. Select: $github_user/bank-fraud-detection"
echo "   6. Click 'Deploy' and wait 2-3 minutes"
echo ""
echo "   Your permanent URL will be shown in the Railway dashboard!"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🎉 You're all set!                                       ║"
echo "║                                                            ║"
echo "║   After Railway deployment, your app will be at:          ║"
echo "║   https://bank-fraud-detection-[random].railway.app      ║"
echo "║                                                            ║"
echo "║   Login with:                                              ║"
echo "║   Email: demo@test.com                                     ║"
echo "║   Password: SecureTest2026!                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
