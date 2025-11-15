#!/bin/bash
# Start both frontend and backend servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Add Homebrew to PATH if it exists
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Starting Mini Search Engine...${NC}\n"

# Check if MongoDB is running (optional)
echo -e "${YELLOW}Checking MongoDB...${NC}"
if pgrep -x "mongod" > /dev/null; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
    MONGO_RUNNING=true
else
    echo -e "${YELLOW}⚠ MongoDB not detected (optional - crawler will work without it)${NC}"
    if command -v brew &> /dev/null; then
        echo -e "${YELLOW}  To install: brew install mongodb-community${NC}"
        echo -e "${YELLOW}  To start: brew services start mongodb-community${NC}"
    fi
    MONGO_RUNNING=false
fi

# Check if data directory exists
if [ ! -d "$PROJECT_ROOT/data_wiki" ]; then
    echo -e "${RED}❌ data_wiki directory not found!${NC}"
    echo -e "${YELLOW}Run the crawler first to generate data${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "\n${BLUE}📡 Starting backend server...${NC}"
cd "$PROJECT_ROOT/backend"

# Load MongoDB configuration if it exists (checks both .env and mongo_config.sh)
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    echo -e "${YELLOW}Loading .env configuration...${NC}"
    # Export all variables from .env file
    set -a
    source "$PROJECT_ROOT/backend/.env"
    set +a
    echo -e "${YELLOW}  MongoDB URI: ${MONGODB_URI:0:30}...${NC}"
    echo -e "${YELLOW}  Use MongoDB: $USE_MONGODB${NC}"
elif [ -f "$PROJECT_ROOT/backend/mongo_config.sh" ]; then
    echo -e "${YELLOW}Loading mongo_config.sh...${NC}"
    source "$PROJECT_ROOT/backend/mongo_config.sh"
else
    # Default settings only if no config files exist
    export DATA_DIR=${DATA_DIR:-../data_wiki}
    export PORT=${PORT:-5001}
    export MONGODB_URI=${MONGODB_URI:-mongodb://localhost:27017/}
    export USE_MONGODB=${USE_MONGODB:-true}
    echo -e "${YELLOW}  Using default configuration${NC}"
    echo -e "${YELLOW}  MongoDB URI: $MONGODB_URI${NC}"
    echo -e "${YELLOW}  Use MongoDB: $USE_MONGODB${NC}"
fi

# Set PORT for backend (allow override from config)
export PORT=${PORT:-5001}

/usr/bin/python3 server.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 3

# Check if backend is running
if ! curl -s http://localhost:5001/api/stats > /dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo -e "${YELLOW}Check backend/server.py for errors${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Backend running on http://localhost:5001${NC}"

# Start frontend
echo -e "\n${BLUE}🎨 Starting frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Set PORT to avoid conflicts
PORT=3000 BROWSER=none npm start &
FRONTEND_PID=$!

echo -e "\n${GREEN}✅ All services started!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend:${NC}  http://localhost:5001"
if [ "$MONGO_RUNNING" = true ]; then
    echo -e "${GREEN}MongoDB:${NC}  Running"
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
