#!/bin/bash

# TrueTank Local Development Server
echo "🚀 Starting TrueTank Development Server..."

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export FLASK_ENV=development
export FLASK_DEBUG=true
export DATABASE_URL=sqlite:///truetank_dev.db
export PORT=5555

# Run the Flask development server
python app.py

echo "👋 TrueTank Development Server stopped."