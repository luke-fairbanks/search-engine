# MongoDB Integration - Summary

## What's New

Your search engine now has full MongoDB integration! Here's what changed:

### ✅ New Files Created

1. **`backend/mongo_search.py`** - MongoDB-based search engine
   - Implements BM25 + PageRank ranking
   - Builds search index from MongoDB documents
   - Automatic index caching and rebuilding
   - Title boosting for better relevance

2. **`backend/mongo_config.sh`** - MongoDB configuration
   - Set your MongoDB connection string here
   - Environment variables for easy setup

3. **`MONGODB_GUIDE.md`** - Complete documentation
   - Setup instructions
   - Usage guide
   - Troubleshooting tips

### 🔧 Modified Files

1. **`backend/server.py`**
   - Uses MongoDB as primary search source
   - Falls back to file-based search if MongoDB unavailable
   - Added `source` field to API responses

2. **`backend/crawler_ws.py`**
   - Improved MongoDB saving logic
   - Updates existing documents instead of duplicates
   - Better snippet extraction
   - More detailed logging

3. **`start.sh`**
   - Loads MongoDB configuration automatically
   - Shows MongoDB status on startup

## How to Use

### 1. Configure MongoDB Connection

Edit `backend/mongo_config.sh` and add your connection string:

```bash
# For local MongoDB (default)
export MONGODB_URI="mongodb://localhost:27017/"

# For MongoDB Atlas (replace with your actual connection string)
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

### 2. Start the Application

```bash
./start.sh
```

The server will automatically connect to MongoDB!

### 3. Crawl with MongoDB

1. Open http://localhost:3000
2. Click the hamburger menu → Crawler
3. **Toggle ON "Save to MongoDB"**
4. Enter a URL and start crawling
5. Pages are saved directly to MongoDB!

### 4. Search Your Data

Just search as normal - it now uses MongoDB by default!

## Key Features

✅ **Real-time indexing** - New pages are searchable immediately
✅ **Smart ranking** - BM25 + PageRank + title boosting
✅ **Automatic fallback** - Uses file-based search if MongoDB unavailable
✅ **Duplicate handling** - Updates existing URLs instead of creating duplicates
✅ **Production-ready** - Works with local MongoDB or MongoDB Atlas

## MongoDB Structure

**Database:** `crawler_db`
**Collection:** `crawled_pages`

Each document:
```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "snippet": "Description...",
  "depth": 0,
  "parent_url": "https://example.com",
  "link_count": 42,
  "links": ["url1", "url2", ...],
  "crawled_at": "2025-11-15T12:00:00Z",
  "start_url": "https://example.com"
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017/` | MongoDB connection string |
| `USE_MONGODB` | `true` | Enable MongoDB (set to `false` for file-based) |
| `DATA_DIR` | `./data` | Fallback data directory |

## What Happens When You Search

1. Query comes in via `/api/search`
2. Server checks if MongoDB is enabled
3. If yes: `MongoSearchEngine.search()` is called
   - Builds/refreshes index from MongoDB
   - Calculates BM25 scores for query terms
   - Calculates PageRank from link structure
   - Applies title matching bonus
   - Combines all signals into final score
4. Returns top K results

## Next Steps

1. **Add your MongoDB connection string** to `backend/mongo_config.sh`
2. **Start the server** with `./start.sh`
3. **Crawl some pages** with "Save to MongoDB" enabled
4. **Search** and see MongoDB-powered results!

## Need Help?

See `MONGODB_GUIDE.md` for:
- Detailed setup instructions
- Troubleshooting guide
- Performance tips
- Architecture diagrams

---

**Note:** The "Save to MongoDB" toggle in the crawler UI now actually works and saves data to your MongoDB database! 🎉
