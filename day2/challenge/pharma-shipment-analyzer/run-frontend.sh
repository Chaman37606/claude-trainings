#!/bin/bash
echo "🚀 Starting Pharma Shipment Risk Analyzer - FRONTEND"
echo "===================================================="
echo ""
echo "Frontend Dashboard will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")/frontend"
npx http-server . -p 3000 -c-1
