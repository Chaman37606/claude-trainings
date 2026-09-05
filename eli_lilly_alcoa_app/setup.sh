#!/bin/bash

# Eli Lilly ALCOA+ QA System Setup Script

echo "🏥 Eli Lilly ALCOA+ QA System Setup"
echo "===================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from database import engine, Base; Base.metadata.create_all(bind=engine); print('✓ Database initialized')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend server:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "2. In another terminal, serve the frontend:"
echo "   python -m http.server 8080"
echo ""
echo "3. Open your browser to: http://localhost:8080"
echo ""
echo "API Documentation: http://localhost:8000/docs"
