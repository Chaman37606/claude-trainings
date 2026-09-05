#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}PHARMA RISK ANALYZER - START${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port 8000 already in use. Killing existing process...${NC}"
    lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
    sleep 1
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port 3000 already in use. Killing existing process...${NC}"
    lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
    sleep 1
fi

echo -e "${GREEN}✓ Ports cleaned${NC}"
echo ""

# Start Backend
echo -e "${BLUE}Starting Backend Server...${NC}"
cd "$(dirname "$0")/backend"
nohup python main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may not be ready yet${NC}"
fi

echo ""

# Start Frontend
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd "$(dirname "$0")/frontend"

# Try http-server first
if command -v http-server &> /dev/null; then
    nohup http-server . -p 3000 -c-1 > /tmp/frontend.log 2>&1 &
else
    # Fallback to Python's built-in server
    nohup python -m http.server 3000 > /tmp/frontend.log 2>&1 &
fi

FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
sleep 2

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ SERVERS RUNNING!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}📊 Dashboard:${NC}"
echo -e "${YELLOW}   http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}🔧 API:${NC}"
echo -e "${YELLOW}   http://localhost:8000/api${NC}"
echo ""
echo -e "${BLUE}📋 API Docs:${NC}"
echo -e "${YELLOW}   http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}✅ Health Check:${NC}"
echo -e "${YELLOW}   http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Keep script running
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT
wait
