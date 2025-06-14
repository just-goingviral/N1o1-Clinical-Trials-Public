#!/bin/bash
# N1O1 Clinical Trials - Unified Startup Script

echo "🚀 Starting N1O1 Clinical Trials Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration values before running again."
    exit 1
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Initialize database if needed
echo "🗄️  Initializing database..."
python -c "from models import init_db; init_db()"

# Start the application
echo "🌟 Starting Flask application on port ${PORT:-5000}..."
python main.py
