#!/bin/bash

# Veo Character Consistency App - Complete Startup Script
# Runs both backend and frontend automatically

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Veo Character Consistency App - Quick Start           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   ./start.sh"
    exit 1
fi

echo "🔍 Checking setup..."
echo ""

# Check backend .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Backend not configured yet${NC}"
    echo ""
    echo "📋 Setup steps:"
    echo "   1. Get Supabase database: https://supabase.com"
    echo "   2. Get Google AI key: https://aistudio.google.com/app/apikey"
    echo "   3. Edit backend/.env with your credentials"
    echo ""
    echo "📖 Read SUPABASE_SETUP.md and GOOGLE_ULTRA_SETUP.md for details"
    echo ""
    exit 1
fi

# Start backend
echo "🚀 Starting backend server..."
cd backend
chmod +x start.sh
./start.sh > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "📋 Check backend.log for errors"
    tail -20 backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend started successfully${NC}"
echo ""

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
chmod +x start.sh
./start.sh > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   🎉 App is Running!                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📍 Frontend:${NC}  http://localhost:3000"
echo -e "${GREEN}📍 API Docs:${NC}  http://localhost:8000/api/v1/docs"
echo -e "${GREEN}📍 Backend:${NC}   http://localhost:8000"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"
echo ""

# Keep script running
wait
