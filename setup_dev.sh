#!/bin/bash

# TrueTank Development Environment Setup
echo "🛠️  Setting up TrueTank Development Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=true
DATABASE_URL=sqlite:///truetank_dev.db
PORT=5555
EOF
fi

echo "✅ Development environment setup complete!"
echo ""
echo "To start the development server, run: ./run_dev.sh"
echo "Or manually: source venv/bin/activate && python app.py"