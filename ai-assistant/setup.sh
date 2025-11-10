#!/bin/bash

# AI Multitask Assistant - Setup Script
# This script sets up the AI assistant environment

set -e  # Exit on error

echo "🤖 AI Multitask Assistant - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required${NC}"
    echo -e "${RED}Current version: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p database
mkdir -p static
mkdir -p templates
mkdir -p n8n_workflows
mkdir -p docs

# Create workspace directory
WORKSPACE_DIR="${HOME}/ai-assistant-workspace"
if [ ! -d "$WORKSPACE_DIR" ]; then
    mkdir -p "$WORKSPACE_DIR"
    echo -e "${GREEN}✓ Workspace directory created at: $WORKSPACE_DIR${NC}"
else
    echo -e "${YELLOW}Workspace directory already exists: $WORKSPACE_DIR${NC}"
fi
echo ""

# Setup environment file
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Update workspace directory in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|WORKSPACE_DIR=.*|WORKSPACE_DIR=$WORKSPACE_DIR|" .env
    else
        # Linux
        sed -i "s|WORKSPACE_DIR=.*|WORKSPACE_DIR=$WORKSPACE_DIR|" .env
    fi
    echo -e "${GREEN}✓ Environment file created (.env)${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your N8N settings if needed${NC}"
else
    echo -e "${YELLOW}.env file already exists. Skipping...${NC}"
fi
echo ""

# Initialize database
echo "Initializing database..."
python -c "from core.database import init_db; init_db()" 2>/dev/null || echo -e "${YELLOW}Database initialization skipped (will be created on first run)${NC}"
echo ""

# Display completion message
echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Start the assistant:"
echo "   ./start.sh"
echo ""
echo "3. Or manually:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "4. Access the web interface at:"
echo "   http://localhost:8001"
echo ""
echo "5. API documentation at:"
echo "   http://localhost:8001/docs"
echo ""
echo "For N8N integration:"
echo "- Install N8N: npm install -g n8n"
echo "- Start N8N: n8n start"
echo "- Import workflows from: n8n_workflows/"
echo ""
echo "Happy automating! 🚀"
