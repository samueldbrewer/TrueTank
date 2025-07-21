#!/bin/bash

# TrueTank Sample Data Deployment to Railway
# This script automates the deployment process

echo "🚀 TrueTank Sample Data Deployment to Railway"
echo "=============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

# Check if sample data file exists
SAMPLE_FILE="sample_data_export_20250711_084627.json"
if [ ! -f "$SAMPLE_FILE" ]; then
    echo "❌ Sample data file not found: $SAMPLE_FILE"
    echo "   Please run: python3 export_sample_data.py"
    exit 1
fi

echo "✅ Found sample data file: $SAMPLE_FILE ($(ls -lh $SAMPLE_FILE | awk '{print $5}'))"

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway first:"
    echo "   railway login"
    exit 1
fi

echo "✅ Railway CLI authenticated ($(railway whoami))"

# Check if project is linked
if railway status 2>&1 | grep -q "No linked project found"; then
    echo "🔗 Please link your Railway project first:"
    echo "   railway link"
    exit 1
fi

# Show current project info
echo "📋 Current Railway Project:"
railway status | grep -E "(Project:|Environment:)"

echo ""
read -p "🚀 Ready to deploy sample data? This will CLEAR existing data. Continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Deploying sample data to Railway..."
echo "⚠️  This will clear existing data and import fresh sample data"
echo ""

# Run the deployment script on Railway
railway run python3 deploy_sample_data.py

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    echo ""
    echo "✅ Sample data deployment completed successfully!"
    echo ""
    echo "🎯 Your Railway database now contains:"
    echo "   • 4 Locations (Pewee Valley, KY)"
    echo "   • 4 Team Members"
    echo "   • 4 Trucks"
    echo "   • 25 Customers"
    echo "   • 18 Septic Systems"
    echo "   • 39 Tickets"
    echo ""
    echo "🌐 Visit your Railway app to test the job board!"
    
    # Try to get the app URL
    if railway status | grep -q "Deployment:"; then
        echo ""
        echo "🔗 Your app should be available at:"
        railway status | grep "Deployment:" | awk '{print $2}'
    fi
else
    echo ""
    echo "❌ Sample data deployment failed!"
    echo "   Check the Railway logs for more details"
    echo "   Or try manual deployment using the Railway dashboard"
    exit 1
fi