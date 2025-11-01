#!/bin/bash

# AgriSense 2.0 Quick Setup Script
# This script sets up the entire AgriSense project

set -e  # Exit on error

echo "========================================"
echo "🌾 AgriSense 2.0 Setup Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "Please install Node.js 18 or higher"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"
echo ""

# Backend setup
echo "========================================"
echo "Setting up Backend..."
echo "========================================"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit backend/.env and add your API keys${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Create data directory
mkdir -p data
mkdir -p chroma_db
mkdir -p cache

cd ..
echo ""

# Frontend setup
echo "========================================"
echo "Setting up Frontend..."
echo "========================================"
cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

cd ..
echo ""

# Summary
echo "========================================"
echo "✨ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Add your Hugging Face API token to backend/.env:"
echo "   ${YELLOW}HF_API_TOKEN=your_token_here${NC}"
echo ""
echo "2. Initialize AgriSense (from backend/ directory):"
echo "   ${GREEN}cd backend${NC}"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo "   ${GREEN}python init_agrisense.py${NC}"
echo ""
echo "3. Start the backend server:"
echo "   ${GREEN}uvicorn main:app --reload${NC}"
echo ""
echo "4. In a new terminal, start the frontend:"
echo "   ${GREEN}cd frontend${NC}"
echo "   ${GREEN}npm run dev${NC}"
echo ""
echo "5. Open http://localhost:5173 in your browser"
echo ""
echo "For more information, see README.md"
echo "========================================"
