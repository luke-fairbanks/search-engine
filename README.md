# Mini Search Engine 🔍

A full-stack search engine with Python backend, React frontend, real-time web crawler, and MongoDB integration. Features BM25 ranking, PageRank, and interactive graph visualization.

## ✨ Features

### 🔍 Search Engine
- **BM25 Ranking** with PageRank integration
- **Title Boosting** for better relevance
- **500 results** with pagination (10 per page)
- **URL state management** (shareable search links)
- **Real-time search** with performance metrics
- **Dark theme** with glassmorphism effects

### 🕷️ Web Crawler
- **Real-time crawling** via WebSocket
- **Interactive graph visualization** (React Flow)
- **Configurable depth** and page limits
- **MongoDB storage** (optional)
- **Live statistics** and progress tracking
- **Domain-restricted** crawling

### 🎨 Modern UI
- **NextUI components** with dark theme
- **Framer Motion** animations
- **Responsive design** with Tailwind CSS
- **Hamburger menu** navigation
- **Collapsible search bar** on focus

## 🚀 Quick Start

### Option 1: Start Everything (Recommended)

```bash
# One command to start both frontend and backend
./start.sh
```

Then open http://localhost:3000 in your browser!

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
export DATA_DIR=../data_wiki PORT=5001
python3 server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## � Installation

### Initial Setup

```bash
# Backend dependencies
cd backend
pip3 install -r requirements.txt

# Frontend dependencies
cd frontend
npm install

# Make scripts executable
chmod +x start.sh setup_mongo.sh
```

### MongoDB Setup (Optional - for Crawler)

```bash
# Run the setup script
./setup_mongo.sh

# Or manually:
brew install mongodb-community
brew services start mongodb-community

# Import existing data
cd backend
python3 import_to_mongo.py --data-dir ../data_wiki
```

## �📁 Project Structure

```
search-engine/
├── backend/                    # Python backend
│   ├── mini_search.py         # Core search (crawler, indexer, ranker)
│   ├── server.py              # Flask REST API + WebSocket
│   ├── crawler_ws.py          # Real-time WebSocket crawler
│   ├── import_to_mongo.py     # MongoDB import script
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchPage.tsx      # Main search interface
│   │   │   ├── CrawlPage.tsx       # Crawler interface
│   │   │   ├── CrawlGraph.tsx      # Graph visualization
│   │   │   ├── Sidebar.tsx         # Navigation menu
│   │   │   └── ...
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   └── package.json          # Node dependencies
├── data_wiki/                  # Wiki crawl data
├── data/                       # Docs crawl data
├── start.sh                    # Start frontend + backend
├── setup_mongo.sh              # MongoDB setup + import
└── CRAWLER_README.md           # Detailed crawler docs
```

## 🎯 Usage

### Search
1. Open http://localhost:3000
2. Enter a search query (e.g., "for loop")
3. Browse paginated results
4. Share the URL with others!

### Crawl
1. Click the **☰ menu** (top-left)
2. Select **"Crawl"**
3. Enter a URL: `https://docs.python.org/3/tutorial/`
4. Configure:
   - Max Depth: 2
   - Max Pages: 50
   - Toggle "Save to MongoDB" (optional)
5. Click **"Start Crawling"**
6. Switch between **Graph View** and **List View**

## Features

- **Web Crawler**: Crawls websites and respects robots.txt
- **BM25 Ranking**: Industry-standard text relevance scoring with title boosting
- **PageRank**: Link analysis algorithm for result ranking
- **Modern UI**: React + TypeScript + NextUI (Hero UI) + Tailwind CSS
- **REST API**: Flask backend with CORS support

## Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Usage
### Step 1: Crawl a Website

```bash
cd backend
python3 mini_search.py crawl --start https://wiki.python.org/moin/BeginnersGuide --max-pages 500 --out ../data_wiki --verbose
```

### Step 2: Build the Index

```bash
python3 mini_search.py build --data ../data_wiki
```

### Step 3: Run the Backend Server

```bash
DATA_DIR=../data_wiki PORT=5001 python3 server.py
```

The API server will start on http://localhost:5001

### Step 4: Run the React Frontend (Development)

In a separate terminal:

```bash
cd frontend
npm start
```

The UI will open at http://localhost:3000

## Production Build

### Build the React app:

```bash
cd frontend
npm run build
cd ..
```

### Run the server (serves both API and static frontend):

```bash
python server.py
```

Visit http://localhost:5000

## API Endpoints

### Search

```
GET /api/search?q=query&alpha=0.2&beta=0.8&k=10
```

Parameters:
- `q`: Search query (required)
- `alpha`: BM25 weight floor (default: 0.2)
- `beta`: PageRank weight (default: 0.8)
- `k`: Number of results (default: 10)

### Stats

```
GET /api/stats
```

Returns index statistics (total docs, vocab size, avg doc length).

## Tech Stack

### Backend
- Python 3
- Flask (HTTP server)
- flask-cors (CORS support)

### Frontend
- React 18
- TypeScript
- Material-UI (MUI)
- Tailwind CSS
- Axios (HTTP client)

## Configuration

Set environment variables:

- `DATA_DIR`: Path to data directory (default: ./data)
- `PORT`: Server port (default: 5000)
- `REACT_APP_API_URL`: API base URL for React app (default: /api)

## License

MIT
