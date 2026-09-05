#!/bin/bash

set -e

echo "🚀 MCP Search Server Setup"
echo "=========================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✓ Node.js $(node -v) detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install
echo "✓ Dependencies installed"
echo ""

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build
echo "✓ Build complete"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (update with your API keys)"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the servers:"
echo ""
echo "Terminal 1 - Start MCP Server:"
echo "  npm start"
echo ""
echo "Terminal 2 - Start Web UI:"
echo "  npm run serve-ui"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"
echo ""
