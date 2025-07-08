#!/bin/bash

# TrueTank Railway Deployment Script
echo "🚀 Deploying TrueTank to Railway..."

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Uncommitted changes found. Committing..."
    git add .
    read -p "Enter commit message: " commit_msg
    git commit -m "$commit_msg"
fi

# Push to Railway
echo "📤 Pushing to Railway..."
git push origin main

echo "✅ Deployment complete!"
echo "🌐 Check your Railway dashboard for deployment status"
echo "🔗 URL: https://truetank-production.up.railway.app"