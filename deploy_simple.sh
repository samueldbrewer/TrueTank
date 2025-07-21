#!/bin/bash

# Simple Railway Deployment (bypasses project linking check)
echo "🚀 Simple Railway Deployment"
echo "============================"

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "❌ Please login first: railway login"
    exit 1
fi

echo "✅ Logged in as: $(railway whoami)"
echo "📁 Sample data file: sample_data_export_20250711_084627.json"
echo ""

read -p "🚀 Deploy sample data to Railway? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

echo "🚀 Deploying..."
railway run python3 deploy_sample_data.py