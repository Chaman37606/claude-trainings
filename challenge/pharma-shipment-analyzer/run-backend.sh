#!/bin/bash
echo "🚀 Starting Pharma Shipment Risk Analyzer - BACKEND"
echo "=================================================="
echo ""
echo "Backend API will run on: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")/backend"
python main.py
