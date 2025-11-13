# Web Crawler Feature 🕷️

A real-time web crawler with graph visualization and MongoDB storage.

## Features

### 🌐 Real-Time Crawling
- Live updates via WebSocket connection
- BFS-based crawling algorithm
- Configurable depth and page limits
- Domain-restricted crawling (stays within same domain)

### 📊 Graph Visualization
- Interactive graph view using React Flow
- Real-time node updates with color-coded status
- Minimap for navigation
- Zoom and pan controls
- Radial layout based on crawl depth

### 💾 MongoDB Integration
- Optional database storage
- Stores crawled pages with metadata
- Includes: URL, title, snippet, depth, links, timestamps
- Organized by crawl session (start_url)

### 📈 Live Statistics
- Total pages crawled
- Completed pages count
- Queue size (pending pages)
- Crawl duration

## Quick Setup

```bash
# Run the setup script
chmod +x setup_crawler.sh
./setup_crawler.sh
```

## Manual Setup

### Backend Dependencies

```bash
cd backend
pip install flask-sock aiohttp beautifulsoup4 simple-websocket

# For MongoDB support (optional)
pip install pymongo motor
```

Or install all at once:
```bash
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd frontend
npm install reactflow
```

### MongoDB Setup (Optional)

**Option 1: Local MongoDB**
```bash
# Install MongoDB (macOS with Homebrew)
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

**Option 2: MongoDB Atlas (Cloud)**
1. Sign up at https://www.mongodb.com/atlas
2. Create a free cluster
3. Get your connection string
4. Set environment variable:
```bash
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/"
```

## Usage

### 1. Start the Backend

```bash
cd backend
export DATA_DIR=../data_wiki
export PORT=5001

# Optional: Set MongoDB connection
export MONGODB_URI="mongodb://localhost:27017/"

python3 server.py
```

You should see:
```
✓ WebSocket crawler enabled
✓ MongoDB connected: mongodb://localhost:27017/
Starting server on http://localhost:5001
```

### 2. Start the Frontend

```bash
cd frontend
npm start
```

### 3. Use the Crawler

1. Click the **hamburger menu (☰)** in the top-left corner
2. Select **"Crawl"** from the sidebar
3. Configure your crawl:
   - **Start URL**: Enter the website to crawl (e.g., `https://docs.python.org/3/`)
   - **Max Depth**: How many levels deep to crawl (default: 2)
   - **Max Pages**: Maximum number of pages to crawl (default: 100)
   - **Save to MongoDB**: Toggle to enable database storage
4. Click **"Start Crawling"**
5. Watch the graph grow in real-time!

### View Options

Switch between two views using the tabs:

- **Graph View**: Interactive visualization of the crawl tree
  - Green nodes = completed
  - Blue pulsing nodes = currently crawling
  - Red nodes = error
  - Gray nodes = pending

- **List View**: Detailed list of crawled pages with metadata

## MongoDB Collections

When MongoDB is enabled, crawled data is stored in:

**Database**: `crawler_db`
**Collection**: `crawled_pages`

**Document Schema**:
```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "snippet": "Meta description...",
  "depth": 1,
  "parent_url": "https://example.com",
  "link_count": 42,
  "links": ["https://example.com/link1", "..."],
  "crawled_at": "2025-11-10T12:34:56Z",
  "start_url": "https://example.com"
}
```

### Query MongoDB

```bash
# Connect to MongoDB
mongosh

# Use the database
use crawler_db

# View all crawls
db.crawled_pages.find()

# Find pages from a specific crawl
db.crawled_pages.find({ "start_url": "https://docs.python.org/3/" })

# Count pages by depth
db.crawled_pages.aggregate([
  { $group: { _id: "$depth", count: { $sum: 1 } } }
])
```

## Architecture

### Frontend
- **React + TypeScript**: Main UI framework
- **React Flow**: Graph visualization library
- **NextUI**: Component library with dark theme
- **Framer Motion**: Smooth animations
- **WebSocket**: Real-time bidirectional communication

### Backend
- **Flask-Sock**: WebSocket server
- **aiohttp**: Async HTTP client for crawling
- **BeautifulSoup4**: HTML parsing
- **Motor**: Async MongoDB driver
- **asyncio**: Async/await pattern for concurrent crawling

### Data Flow
```
User Input → WebSocket → Crawler → BeautifulSoup → Links
                ↓                        ↓
            Frontend Graph          MongoDB (optional)
```

## Configuration

### Environment Variables

```bash
# Backend server port
export PORT=5001

# Data directory for search index
export DATA_DIR=../data_wiki

# MongoDB connection string (optional)
export MONGODB_URI="mongodb://localhost:27017/"
# Or for MongoDB Atlas:
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
```

### Crawler Settings

Adjust in the UI:
- **Max Depth**: Limits crawl depth (1-5 recommended)
- **Max Pages**: Prevents infinite crawls (10-1000 range)
- **Save to MongoDB**: Toggle database storage

## Troubleshooting

### "WebSocket crawler disabled"
```bash
# Install missing dependencies
pip install flask-sock aiohttp beautifulsoup4 simple-websocket
```

### "MongoDB connection failed"
- Check if MongoDB is running: `brew services list`
- Verify connection string in `MONGODB_URI`
- Try default: `mongodb://localhost:27017/`

### Graph not rendering
```bash
# Reinstall React Flow
cd frontend
npm install reactflow --force
```

### Crawl is slow
- Reduce `Max Pages` to a smaller number
- Decrease `Max Depth` to 1 or 2
- Check network connectivity to target site

## Future Enhancements

- [ ] Export crawl results to JSON/CSV
- [ ] Resume interrupted crawls
- [ ] URL pattern filters (include/exclude)
- [ ] Parallel crawling with worker pools
- [ ] Crawl scheduling and recurring jobs
- [ ] Advanced graph layouts (hierarchical, force-directed)
- [ ] Page content analysis and keyword extraction
- [ ] Duplicate detection and URL normalization
- [ ] Robots.txt compliance
- [ ] Rate limiting and politeness delays

## Performance Tips

1. **Start small**: Test with max 10-20 pages first
2. **Choose depth wisely**: Depth 2-3 is usually sufficient
3. **Use MongoDB**: For large crawls (100+ pages)
4. **Monitor queue**: Stop if queue grows too large
5. **Respect target sites**: Don't crawl too aggressively

## Examples

### Small Focused Crawl
```
URL: https://docs.python.org/3/tutorial/
Max Depth: 2
Max Pages: 50
```

### Documentation Crawl
```
URL: https://react.dev/
Max Depth: 3
Max Pages: 200
Save to MongoDB: ✓
```

### Quick Test
```
URL: https://example.com
Max Depth: 1
Max Pages: 10
```

## Support

For issues or questions, check:
- Backend logs in the terminal running `server.py`
- Frontend console in browser DevTools (F12)
- MongoDB logs: `tail -f /usr/local/var/log/mongodb/mongo.log`
