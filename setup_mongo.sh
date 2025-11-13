#!/bin/bash
# Setup MongoDB and import existing data

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🗄️  MongoDB Setup for Mini Search Engine${NC}\n"

# Add Homebrew to PATH if it exists
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo -e "${YELLOW}MongoDB not installed. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Error: Homebrew not found${NC}"
            echo -e "${YELLOW}Please install Homebrew first: https://brew.sh${NC}"
            echo -e "${YELLOW}Or install MongoDB manually: https://www.mongodb.com/docs/manual/installation/${NC}"
            exit 1
        fi
        # macOS
        brew tap mongodb/brew
        brew install mongodb-community
    else
        echo -e "${RED}Please install MongoDB manually for your OS${NC}"
        echo "Visit: https://www.mongodb.com/docs/manual/installation/"
        exit 1
    fi
fi

echo -e "${GREEN}✓ MongoDB installed${NC}"

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${YELLOW}Starting MongoDB...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start mongodb-community
        sleep 3
    else
        echo -e "${YELLOW}Please start MongoDB manually:${NC}"
        echo "  sudo systemctl start mongod"
        exit 1
    fi
fi

# Verify MongoDB is running
if pgrep -x "mongod" > /dev/null; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "${RED}❌ Failed to start MongoDB${NC}"
    exit 1
fi

# Import data_wiki
echo -e "\n${BLUE}📥 Importing data_wiki to MongoDB...${NC}"
cd backend
/usr/bin/python3 import_to_mongo.py --data-dir ../data_wiki

# Import data (if exists)
if [ -d "../data" ]; then
    echo -e "\n${BLUE}📥 Importing data to MongoDB...${NC}"
    /usr/bin/python3 import_to_mongo.py --data-dir ../data
fi

echo -e "\n${GREEN}✅ MongoDB setup complete!${NC}"
echo -e "\n${BLUE}Quick commands:${NC}"
echo -e "  mongosh                    # Connect to MongoDB"
echo -e "  use crawler_db             # Select database"
echo -e "  db.crawled_pages.find()    # View documents"
echo -e "  db.crawled_pages.count()   # Count documents"
