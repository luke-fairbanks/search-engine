# MongoDB Import & Startup Guide

## Import Existing Data to MongoDB

You have two data directories that can be imported:
- `data_wiki/` - Python wiki pages
- `data/` - Python docs pages

### Automatic Import (Recommended)

```bash
# This will:
# 1. Install/start MongoDB
# 2. Import both data directories
./setup_mongo.sh
```

### Manual Import

**Start MongoDB:**
```bash
brew services start mongodb-community
```

**Import data_wiki:**
```bash
cd backend
python3 import_to_mongo.py --data-dir ../data_wiki
```

**Import data:**
```bash
python3 import_to_mongo.py --data-dir ../data
```

## Start Frontend & Backend

### All-in-One (Recommended)

```bash
# From project root
./start.sh
```

This will:
- ✓ Check MongoDB status
- ✓ Start backend on port 5001
- ✓ Start frontend on port 3000
- ✓ Open browser automatically
- ✓ Handle shutdown gracefully (Ctrl+C)

### Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
export DATA_DIR=../data_wiki
export PORT=5001
export MONGODB_URI=mongodb://localhost:27017/
python3 server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## Verify MongoDB Import

```bash
# Connect to MongoDB shell
mongosh

# Use the database
use crawler_db

# Count documents
db.crawled_pages.count()

# View sample documents
db.crawled_pages.find().limit(5).pretty()

# View by source
db.crawled_pages.distinct("start_url")

# Pages by depth
db.crawled_pages.aggregate([
  { $group: { _id: "$depth", count: { $sum: 1 } } },
  { $sort: { _id: 1 } }
])
```

## Troubleshooting

### MongoDB won't start
```bash
# Check status
brew services list

# Restart
brew services restart mongodb-community

# Check logs
tail -f /usr/local/var/log/mongodb/mongo.log
```

### Import fails
```bash
# Check if MongoDB is running
pgrep mongod

# Check if data directory exists
ls -la data_wiki/

# Try with verbose output
python3 import_to_mongo.py --data-dir ../data_wiki --mongo-uri mongodb://localhost:27017/
```

### Backend won't start
```bash
# Check if port 5001 is in use
lsof -i :5001

# Kill process on port 5001
kill -9 $(lsof -ti:5001)

# Check dependencies
pip3 install -r requirements.txt
```

### Frontend won't start
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is in use
lsof -i :3000
```

## Expected Output

### MongoDB Import
```
🔌 Connecting to MongoDB: mongodb://localhost:27017/
✓ Connected to MongoDB
📊 Crawl source: https://wiki.python.org/
📅 Crawled at: 2025-11-10
📄 Found 500 pages to import
📥 Importing pages...
  ✓ Imported 500/500 pages
✅ Import complete!
   Imported: 500 pages
   Errors: 0
```

### Startup Script
```
🚀 Starting Mini Search Engine...

Checking MongoDB...
✓ MongoDB is running

📡 Starting backend server...
✓ WebSocket crawler enabled
✓ MongoDB connected: mongodb://localhost:27017/
✓ Backend running on http://localhost:5001

🎨 Starting frontend...

✅ All services started!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend: http://localhost:3000
Backend:  http://localhost:5001
MongoDB:  Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press Ctrl+C to stop all services
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `./start.sh` | Start frontend + backend |
| `./setup_mongo.sh` | Setup MongoDB + import data |
| `mongosh` | Connect to MongoDB |
| `Ctrl+C` | Stop all services |
| `brew services list` | Check MongoDB status |
| `lsof -i :5001` | Check backend port |
| `lsof -i :3000` | Check frontend port |
