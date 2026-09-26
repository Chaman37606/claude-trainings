#!/bin/bash

echo "🚀 Pharma Shipment Risk Analyzer - Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python $(python3 --version)"

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Backend dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

cd ..

# Create uploads directory
mkdir -p backend/uploads
echo "✓ Created uploads directory"

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "API_PORT=8000
UI_PORT=3000" > .env
    echo "✓ Created .env file"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend && python main.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend && npx http-server . -p 3000"
echo ""
echo "Then open: http://localhost:3000"
echo ""
