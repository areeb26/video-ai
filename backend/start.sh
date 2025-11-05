#!/bin/bash

# Veo Character Consistency App - Easy Start Script
# This script sets up and runs the backend server

echo "🚀 Starting Veo Character Consistency Backend..."
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the 'backend' directory"
    echo "   cd backend && ./start.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/.installed" ]; then
    echo "📚 Installing dependencies (this may take 5-10 minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.installed
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit backend/.env and add:"
    echo "   1. Your Supabase DATABASE_URL"
    echo "   2. Your GOOGLE_AI_API_KEY"
    echo ""
    echo "   Then run this script again: ./start.sh"
    echo ""
    exit 1
fi

# Check if required env vars are set
source .env
if [ -z "$DATABASE_URL" ] || [ "$DATABASE_URL" = "postgresql://user:password@localhost:5432/video_ai_db" ]; then
    echo "⚠️  Warning: DATABASE_URL not configured in .env"
    echo "   Please add your Supabase connection string"
    exit 1
fi

if [ -z "$GOOGLE_AI_API_KEY" ] || [ "$GOOGLE_AI_API_KEY" = "your_google_ai_api_key_here" ]; then
    echo "⚠️  Warning: GOOGLE_AI_API_KEY not configured in .env"
    echo "   Please add your Google AI API key"
    exit 1
fi

# Create upload directories
mkdir -p uploads media

echo ""
echo "✨ Starting backend server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/api/v1/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
cd app
python main.py
