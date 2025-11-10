#!/bin/bash

# AI Multitask Assistant - Start Script
# This script starts the AI assistant server

set -e  # Exit on error

echo "🤖 Starting AI Multitask Assistant..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your configuration${NC}"
fi

# Start the server
echo -e "${GREEN}Starting server...${NC}"
echo ""
echo "Access the assistant at:"
echo "  Web Interface: http://localhost:8001"
echo "  API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the application
python main.py
