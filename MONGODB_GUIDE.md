# MongoDB Integration Guide

This search engine now supports MongoDB as the primary data source! The crawler can save pages directly to MongoDB, and searches are performed against the MongoDB database.

## Quick Start

### 1. Set Your MongoDB Connection String

Edit `backend/mongo_config.sh` and set your MongoDB URI:

```bash
# For local MongoDB
export MONGODB_URI="mongodb://localhost:27017/"

# For MongoDB Atlas (cloud)
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

### 2. Load the Configuration

```bash
cd backend
source mongo_config.sh
```

### 3. Start the Server

```bash
python server.py
```

The server will automatically:
- ✓ Connect to MongoDB
- ✓ Use MongoDB as the primary search source
- ✓ Fall back to file-based search if MongoDB is unavailable

## Using the Crawler with MongoDB

1. **Start the server** (see above)
2. **Open the web UI** at http://localhost:5000
3. **Navigate to the Crawler page** (hamburger menu → Crawler)
4. **Enable "Save to MongoDB"** toggle
5. **Enter a URL and start crawling**

The crawler will save all crawled pages directly to MongoDB!

## MongoDB Collections

### Database: `crawler_db`
### Collection: `crawled_pages`

Each document contains:
```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "snippet": "Page description or first paragraph...",
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
| `USE_MONGODB` | `true` | Enable/disable MongoDB (set to `false` to use files) |
| `DATA_DIR` | `./data` | Directory for file-based fallback |

## Search Features

The MongoDB-based search engine provides:

✓ **BM25 Ranking** - Industry-standard text relevance scoring
✓ **PageRank** - Link-based importance scoring
✓ **Title Boosting** - Extra weight for matches in titles/URLs
✓ **Real-time Indexing** - Index rebuilds automatically when new pages are added
✓ **Hybrid Scoring** - Combines multiple signals for better results

## Importing Existing Data

If you have existing crawled data in JSON files, import it to MongoDB:

```bash
python import_to_mongo.py
```

This will import all pages from `./data/pages/` into MongoDB.

## Switching Between MongoDB and Files

### Use MongoDB (default):
```bash
export USE_MONGODB="true"
python server.py
```

### Use Files:
```bash
export USE_MONGODB="false"
python server.py
```

## Troubleshooting

### "MongoDB search engine failed to initialize"
- Check your MongoDB connection string
- Ensure MongoDB is running (local) or accessible (cloud)
- Verify your credentials for MongoDB Atlas

### "No data source available"
- Either crawl some pages with MongoDB enabled, OR
- Run `python mini_search.py build --data ./data` to build file-based index

### No search results
- Crawl some pages first using the web UI
- Check MongoDB has documents: `db.crawled_pages.count()` in mongo shell
- Try rebuilding the index by restarting the server

## Performance Tips

1. **Index your MongoDB collection** for better search performance:
   ```javascript
   db.crawled_pages.createIndex({ url: 1 }, { unique: true })
   db.crawled_pages.createIndex({ start_url: 1 })
   db.crawled_pages.createIndex({ crawled_at: -1 })
   ```

2. **Use MongoDB Atlas** for production deployments
3. **Adjust crawler settings** to avoid overwhelming your database:
   - Lower max_pages for initial testing
   - Use appropriate max_depth (2-3 recommended)

## Architecture

```
┌─────────────┐
│  Web UI     │
│  (React)    │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       │
┌──────▼──────────────────────────┐
│  Flask Server (server.py)       │
│  ┌────────────┐  ┌────────────┐ │
│  │ REST API   │  │ WebSocket  │ │
│  │ /api/search│  │ /ws/crawl  │ │
│  └─────┬──────┘  └──────┬─────┘ │
└────────┼─────────────────┼───────┘
         │                 │
         │                 │
    ┌────▼────┐       ┌────▼────────┐
    │ MongoDB │◄──────┤  Crawler    │
    │ Search  │       │  (crawler_  │
    │ Engine  │       │   ws.py)    │
    └─────────┘       └─────────────┘
         │
         │
    ┌────▼──────────┐
    │   MongoDB     │
    │   crawler_db  │
    │   .crawled_   │
    │    pages      │
    └───────────────┘
```

## Next Steps

1. Set your MongoDB connection string in `mongo_config.sh`
2. Source the config: `source backend/mongo_config.sh`
3. Start crawling with MongoDB enabled!
4. Search your crawled data in real-time

Enjoy your MongoDB-powered search engine! 🚀
